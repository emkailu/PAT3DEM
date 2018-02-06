echo '''motioncor2 \
-InMrc      BCM_MS2-pox38-tilt_0945_Aug04.mrc               \
-OutMrc     Corrected_BCM_MS2-pox38-tilt_0945_Aug04.mrc     \
-Serial     0           \
-Patch      5  5        \
-Iter       10          \
-Tol        0.5         \
-Bft        100         \
-FtBin      2           \
-InitDose   0           \
-FmDose     0.925375    \
-PixSize    0.615       \
-kV         300         \
-Throw      0           \
-Trunc      0           \
-Group      1           \
-FmRef      21          \
-OutStack   1           \
-Tilt       30  0
'''
