# Music Structure Analysis Framework #

A Python framework to analyze music structure.

* Master branch: [![Build Status](https://travis-ci.org/urinieto/msaf.svg?branch=master)](https://travis-ci.org/urinieto/msaf)
* Devel branch: [![Build Status](https://travis-ci.org/urinieto/msaf.svg?branch=devel)](https://travis-ci.org/urinieto/msaf)

## Description ##

This framework contains a set of algorithms to segment a given music audio signal into its different musical sections (e.g., verse, chorus). It uses [librosa](https://github.com/bmcfee/librosa/) to extract the audio features, [JAMS](https://github.com/urinieto/jams) to read and write references and estimations respectively, and [mir_eval](https://github.com/craffel/mir_eval) to evaluate the estimations.

Two types of algorithms are included in MSAF:
* Boundary Algorithms: Aim to identify the segment boundaries of a given audio signal.
* Labeling (or Structural Grouping) Algorithms: Aim to cluster the different music segments defined by the previously detected boundaries based on their acoustic similarity.

(**Note**: Additional algorithms can be found in the [msaf-gpl](https://github.com/urinieto/msaf-gpl) package.)

## Boundary Algorithms ##

* Improved C-NMF (Nieto & Jehan 2013)
* Checkerboard-like Kernel (Foote 2000)
* OLDA (McFee & Ellis 2014) (original source code from [here](https://github.com/bmcfee/olda))
* Spectral Clustering (McFee & Ellis 2014) (original source code from [here](https://github.com/bmcfee/laplacian_segmentation))
* Structural Features (Serrà et al. 2012)

## Labeling Algorithms ##

* Improved C-NMF (Nieto & Jehan 2013)
* 2D Fourier Magnitude Coefficients (Nieto & Bello 2014)
* Spectral Clustering (McFee & Ellis 2014) (original source code from [here](https://github.com/bmcfee/laplacian_segmentation))

## Installing MSAF #

From the root folder, type:
    
    python setup.py install

(Note: you may need to prefix the previous line with `sudo`, depending on your system configuration).

## Using MSAF ##

A series of examples can be seen in the `examples` folder.

You can follow a thorough example on this fantastic [Jupyter Notebook](https://github.com/urinieto/msaf/blob/master/examples/Run%20MSAF.ipynb).

MSAF can be run in two different modes: **single file** and **collection** modes.

###Single File Mode###

To run an audio file with the Convex NMF method for boundaries and 2D-FMC for labels using HPCP as features (from the `examples` folder):

    ./run_msaf.py audio_file.mp3 -bid cnmf -lid fmc2d -f hpcp

The input file can be of type `mp3`, `wav` or `aif`.

If you want to *sonify* the boundaries, add the `-s` flag, and a file called `out_boundaries.wav` will be created in your current folder.

If you want to plot the boundaries against the ground truth, add the `-p` (only if ground truth references are available).

For more info, type:

    ./run_msaf.py -h


###Collection Mode###

You can run MSAF on a collection of files by inputting the correctly formatted folder to the dataset.
In this mode, MSAF will precompute the features during the first run and put them in a specific folder in order to speed up the process in further runnings.
After running the collection, you can also evaluate it using the standard music segmentation evaluation metrics (as long as you have reference annotations for it).

####Running Collection####

The MSAF datasets should have the following folder structure:

    my_collection/
    ├──  audio: The audio files of your collection.
    ├──  estimations: Estimations (output) by MSAF. Should be empty initially.
    ├──  features: Feature files for speeding up running time. Should be empty initially.
    └──  references: Human references for evaluation purposes.

There are multiple examples of datasets in the `datasets` folder.
Moreover, a complete dataset composed of 4 tracks is found in the `datasets/Sargon`.
We will use it here as an example.

To run the Foote algorithm for boundaries on the Sargon dataset with mfcc as features, we can type:

    ./run_msaf.py ../datasets/Sargon -f mfcc -bid foote

Furthermore, we can spread the work across multiple processors by using the `-j` flag.
By default the number of processors is 1, this can be explicitly set by typing:

    ./run_msaf.py ../datasets/Sargon -f mfcc -bid foote -j 8

For more information, please type:

    ./run_msaf.py -h

####Evaluating Collection####

When running a collection, the evaluation is automatically computed once the estimations are produced.
However, you might want to evaluate a set of previously estimated results.
To do so, simply add the flag `-e`.

    ./run_msaf.py ../datasets/Sargon -f mfcc -bid foote

The output contains the following evaluation metrics:

| Metric        | Description       |
| --------------|-------------------|
| D             | Information Gain  |
| DevE2R        | Median Deviation from Estimation to Reference |
| DevR2E        | Median Deviation from Reference to Estimation |
| DevtE2R       | Median Deviation from Estimation to Reference without first and last boundaries (trimmed)|
| DevtR2E       | Median Deviation from Reference to Estimation without first and last boundaries (trimmed)|
| HitRate\_0.5F | Hit Rate F-measure using 0.5 seconds window |
| HitRate\_0.5P | Hit Rate Precision using 0.5 seconds window |
| HitRate\_0.5R | Hit Rate Recall using 0.5 seconds window |
| HitRate\_3F | Hit Rate F-measure using 3 seconds window |
| HitRate\_3P | Hit Rate Precision using 3 seconds window |
| HitRate\_3R | Hit Rate Recall using 3 seconds window |
| HitRate\_t0.5F | Hit Rate F-measure using 0.5 seconds window without first and last boundaries (trimmed)|
| HitRate\_t0.5P | Hit Rate Precision using 0.5 seconds window without first and last boundaries (trimmed)|
| HitRate\_t0.5R | Hit Rate Recall using 0.5 seconds window without first and last boundaries (trimmed)|
| HitRate\_t3F | Hit Rate F-measure using 3 seconds window without first and last boundaries (trimmed)|
| HitRate\_t3P | Hit Rate Precision using 3 seconds window without first and last boundaries (trimmed)|
| HitRate\_t3R | Hit Rate Recall using 3 seconds window without first and last boundaries (trimmed)|
| PWF           | Pairwise Frame Clustering F-measure |
| PWP           | Pairwise Frame Clustering Precision |
| PWR           | Pairwise Frame Clustering Recall |
| Sf           | Normalized Entropy Scores F-measure |
| So           | Normalized Entropy Scores Precision |
| Su           | Normalized Entropy Scores Recall |


Please, note that before you can use the `-e` flag (i.e., evaluate some results) on a specific feature and set of algorithms, you **must** have run the `run_msaf.py` script first without this flag.

For more information about the metrics read the segmentation metrics in the [MIREX website](http://www.music-ir.org/mirex/wiki/2014:Structural_Segmentation).

###As a Python module###

The main function is `process`, which takes basically the same parameters as the `run_msaf.py` script, and it returns the estimated boundary times and labels.

As an example:

```python
import msaf
estimations = msaf.process("../datasets/Sargon/audio/01-Sargon-Mindless.mp3", feature="hpcp", boundaries_id="cnmf", labels_id="cnmf")
est_boundary_times = estimations[0]
est_labels = estimations[1]
```

For more parameters, please read the function's docstring.
For more examples, please explore the `examples` folder.


## Requirements ##

* Python 2.7 or 3.4
* Numpy
* Scipy
* cvxopt (for C-NMF algorithms only)
* Pandas (for evaluation only)
* joblib
* [mir\_eval](https://github.com/craffel/mir_eval)
* [librosa](https://github.com/bmcfee/librosa/) (>=0.4.0rc1)
* BLAS and LAPACK (Linux Only, OSX will use Accelerate by default)
* ffmpeg (to read mp3 files only)


## Note on Parallel Processes for OSX Users ##

By default, Numpy is compiled against the Accelerate Framework by Apple.
While this framework is extremely fast, Apple [does not want you to fork()
without exec](http://mail.scipy.org/pipermail/numpy-discussion/2012-August/063589.html), which may result in nasty crashes when using more than one thread (`-j > 1`).

The solution is to use an alternative framework, like OpenBLAS, and link it to
Numpy instead of the Accelerate Framework.
There is a nice explanation to do so [here](http://stackoverflow.com/a/14391693/777706).

## References ##

Foote, J. (2000). Automatic Audio Segmentation Using a Measure Of Audio Novelty. In Proc. of the IEEE International Conference of Multimedia and Expo (pp. 452–455). New York City, NY, USA.

Humphrey, E. J., Salamon, J., Nieto, O., Forsyth, J., Bittner, R. M., & Bello, J. P. (2014). JAMS: A JSON Annotated Music Specification for Reproducible MIR Research. In Proc. of the 15th International Society for Music Information Retrieval Conference. Taipei, Taiwan.

Levy, M., & Sandler, M. (2008). Structural Segmentation of Musical Audio by Constrained Clustering. IEEE Transactions on Audio, Speech, and Language Processing, 16(2), 318–326. doi:10.1109/TASL.2007.910781

McFee, B., & Ellis, D. P. W. (2014). Learnign to Segment Songs With Ordinal Linear Discriminant Analysis. In Proc. of the 39th IEEE International Conference on Acoustics Speech and Signal Processing (pp. 5197–5201). Florence, Italy.

Mcfee, B., & Ellis, D. P. W. (2014). Analyzing Song Structure with Spectral Clustering. In Proc. of the 15th International Society for Music Information Retrieval Conference (pp. 405–410). Taipei, Taiwan.

Nieto, O., & Bello, J. P. (2014). Music Segment Similarity Using 2D-Fourier Magnitude Coefficients. In Proc. of the 39th IEEE International Conference on Acoustics Speech and Signal Processing (pp. 664–668). Florence, Italy.

Nieto, O., & Jehan, T. (2013). Convex Non-Negative Matrix Factorization For Automatic Music Structure Identification. In Proc. of the 38th IEEE International Conference on Acoustics Speech and Signal Processing (pp. 236–240). Vancouver, Canada.

Raffel, C., Mcfee, B., Humphrey, E. J., Salamon, J., Nieto, O., Liang, D., & Ellis, D. P. W. (2014). mir_eval: A Transparent Implementation of Common MIR Metrics. In Proc. of the 15th International Society for Music Information Retrieval Conference. Taipei, Taiwan.

Serrà, J., Müller, M., Grosche, P., & Arcos, J. L. (2014). Unsupervised Music Structure Annotation by Time Series Structure Features and Segment Similarity. IEEE Transactions on Multimedia, Special Issue on Music Data Mining, 16(5), 1229 – 1240. doi:10.1109/TMM.2014.2310701

Weiss, R., & Bello, J. P. (2011). Unsupervised Discovery of Temporal Structure in Music. IEEE Journal of Selected Topics in Signal Processing, 5(6), 1240–1251.

## Credits ##

Created by [Oriol Nieto](http://marl.smusic.nyu.edu/nieto/) (<oriol@nyu.edu>).
