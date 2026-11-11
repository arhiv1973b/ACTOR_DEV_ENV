# Carousel Rotation Engine - Apostille Archive

## Logic
1.  **Monitor**: The repository size is monitored.
2.  **Threshold**: 2GB max (strictly GitHub limit).
3.  **Action**: If size > 2GB, the oldest file from the 1-90 registry is automatically deleted (FIFO).
4.  **Verification**: New files are added only when space is confirmed.
