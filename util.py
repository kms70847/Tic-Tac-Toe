def make2dArray(width, height, defaultValue=None):
    return [[defaultValue for j in range(height)] for i in range(width)]