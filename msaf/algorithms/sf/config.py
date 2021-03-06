"""Config for the Structural Features algorithm."""

# Serra params
config = {
    "M_gaussian"    : 23,
    "m_embedded"    : 3,
    "k_nearest"     : 0.04,
    "Mp_adaptive"   : 28,
    "offset_thres"  : 0.05

    # For framesync features
    #"M_gaussian"    : 100,
    #"m_embedded"    : 3,
    #"k_nearest"     : 0.06,
    #"Mp_adaptive"   : 100,
    #"offset_thres"  : 0.01
}

algo_id = "sf"
is_boundary_type = True
is_label_type = False
