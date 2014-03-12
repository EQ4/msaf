#!/usr/bin/env python
# coding: utf-8
"""
This script identifies the boundaries of a given track using the Serrà
method:

Serrà, J., Müller, M., Grosche, P., & Arcos, J. L. (2012). Unsupervised 
Detection of Music Boundaries by Time Series Structure Features. 
In Proc. of the 26th AAAI Conference on Artificial Intelligence (pp. 1613–1619). 
Toronto, Canada.
"""

__author__ = "Oriol Nieto"
__copyright__ = "Copyright 2014, Music and Audio Research Lab (MARL)"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "oriol@nyu.edu"

import argparse
import glob
import jams
import logging
import os
import pylab as plt
import numpy as np
import time
import librosa
import mir_eval
from scipy.spatial import distance
from scipy import signal
from scipy.ndimage import filters
from skimage.filter import threshold_adaptive

import sys
sys.path.append( "../../" )
import msaf_io as MSAF
import utils as U


def median_filter(X, M=8):
    """Median filter along the first axis of the feature matrix X."""
    for i in xrange(X.shape[1]):
        X[:,i] = filters.median_filter(X[:,i], size=M)
    return X

def gaussian_filter(X, M=8, axis=0):
    """Gaussian filter along the first axis of the feature matrix X."""
    for i in xrange(X.shape[axis]):
        if axis == 1:
            X[:,i] = filters.gaussian_filter(X[:,i], sigma=M/2.)
        elif axis == 0:
            X[i,:] = filters.gaussian_filter(X[i,:], sigma=M/2.)
    return X    

def compute_gaussian_krnl(M):
    """Creates a gaussian kernel following Serra's paper."""
    g = signal.gaussian(M, M/3., sym=True)
    G = np.dot(g.reshape(-1,1), g.reshape(1,-1))
    G[M/2:,:M/2] = -G[M/2:,:M/2]
    G[:M/2,M/2:] = -G[:M/2,M/2:]
    return G


def compute_ssm(X, metric="seuclidean"):
    """Computes the self-similarity matrix of X."""
    D = distance.pdist(X, metric=metric)
    D = distance.squareform(D)
    D /= D.max()
    return 1-D

def compute_nc(X):
    """Computes the novelty curve from the structural features."""
    N = X.shape[0]
    # nc = np.sum(np.diff(X, axis=0), axis=1) # Difference between SF's

    nc = np.zeros(N)
    for i in xrange(N-1):
        nc[i] = distance.euclidean(X[i,:], X[i+1,:])

    # Normalize
    nc += np.abs(nc.min())
    nc /= nc.max()
    return nc

def pick_peaks(nc, L=16, offset_denom=0.1):
    """Obtain peaks from a novelty curve using an adaptive threshold."""
    offset = nc.mean() * float(offset_denom)
    th = filters.median_filter(nc, size=L) + offset
    #th = filters.gaussian_filter(nc, sigma=L/2., mode="nearest") + offset
    # plt.plot(nc)
    # plt.plot(th)
    # plt.show()
    peaks = []
    for i in xrange(1,nc.shape[0]-1):
        # is it a peak?
        if nc[i-1] < nc[i] and nc[i] > nc[i+1]:
            # is it above the threshold?
            if nc[i] > th[i]:
                peaks.append(i)
    return peaks

def circular_shift(X):
    """Shifts circularly the X squre matrix in order to get a 
        time-lag matrix."""
    N = X.shape[0]
    L = np.zeros(X.shape)
    for i in xrange(N):
        L[i,:] = np.asarray([X[(i + j) % N,j] for j in xrange(N)])
    return L


def process(in_path, feature="hpcp", annot_beats=False):
    """Main process."""

    # Serra's params
    M = 16      # Size of gaussian kernel
    m = 1       # Size of median filter
    k = 0.7       # Amount of nearest neighbors for the reccurrence plot
    Mp = 8     # Size of the adaptive threshold for peak picking
    od = 0.01    # Offset coefficient for adaptive thresholding

    # Read features
    chroma, mfcc, beats, dur = MSAF.get_features(in_path, 
                                                    annot_beats=annot_beats)

    # Use specific feature
    if feature == "hpcp":
        F = U.lognormalize_chroma(chroma) #Normalize chromas
    elif "mfcc":
        F = mfcc
    else:
        logging.error("Feature type not recognized: %s" % feature)

    # Median filter
    F = median_filter(F, M=m)
    # F = gaussian_filter(F, M=2, axis=1)
    # plt.imshow(F.T, interpolation="nearest", aspect="auto"); plt.show()

    # Self similarity matrix
    #S = compute_ssm(F)

    # Recurrence matrix
    R = librosa.segment.recurrence_matrix(F.T, 
                                          k=k * \
                                            int(np.floor(np.sqrt(F.shape[0]))), 
                                          width=5, # zeros from the diagonal
                                          metric="seuclidean",
                                          sym=False).astype(np.float32)

    # Circular shift
    L = circular_shift(R)
    # plt.imshow(R, interpolation="nearest", aspect="auto"); plt.show()

    # Obtain structural features by filtering the lag matrix
    SF = gaussian_filter(L.T, M=M, axis=1)
    # SF = gaussian_filter(L.T, M=2, axis=0)
    # plt.imshow(SF.T, interpolation="nearest", aspect="auto"); plt.show()

    # Compute the novelty curve
    nc = compute_nc(SF)

    # Read annotated bounds for comparison purposes
    ann_bounds = MSAF.read_annot_bound_frames(in_path, beats)
    logging.info("Annotated bounds: %s" % ann_bounds)

    # Find peaks in the novelty curve
    est_bounds = pick_peaks(nc, L=Mp, offset_denom=od)

    # Concatenate first and last boundaries
    est_bounds = np.concatenate(([0], est_bounds, [F.shape[0]-1])).astype(int)
    logging.info("Estimated bounds: %s" % est_bounds)

    # Get times
    est_times = beats[est_bounds]

    return est_times


    # plt.figure(1)
    # plt.plot(nc); 
    # [plt.axvline(p, color="m") for p in est_bounds]
    # [plt.axvline(b, color="g") for b in ann_bounds]
    # plt.figure(2)
    # plt.imshow(S, interpolation="nearest", aspect="auto")
    # [plt.axvline(b, color="g") for b in ann_bounds]
    # plt.show()


def main():
    """Main function to parse the arguments and call the main process."""
    parser = argparse.ArgumentParser(description=
        "Segments the given audio file using the Serrà's method.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("in_path",
                        action="store",
                        help="Input path to the audio file")
    parser.add_argument("-f", 
                        action="store", 
                        dest="feature",
                        help="Feature to use (mfcc or hpcp)",
                        default="hpcp")
    parser.add_argument("-b", 
                        action="store_true", 
                        dest="annot_beats",
                        help="Use annotated beats",
                        default=False)
    args = parser.parse_args()
    start_time = time.time()
   
    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
        level=logging.INFO)

    # Run the algorithm
    process(args.in_path, feature=args.feature, annot_beats=args.annot_beats)

    # Done!
    logging.info("Done! Took %.2f seconds." % (time.time() - start_time))

if __name__ == '__main__':
    main()