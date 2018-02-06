#!/bin/bash

cat run1_ct16_data.star |awk '{if (NF<3) {print} else {if ($15 > 100 || $15 < -110) print}}' >rot_gt100_lt-100_-60to50.star
cat run1_ct16_data.star |awk '{if ($15 > -60 && $15 < 50) print}' >>rot_gt100_lt-100_-60to50.star