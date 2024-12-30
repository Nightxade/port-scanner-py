def ljust_all(strs: list, width: int | list, fillchar: str=' ', delimiter: str='') -> str:
    '''
    Executes ljust on all provided strings
        strs: list of strings to perform ljust on
        width: width to pass to ljust, list of widths to pass to ljust
        fillchar: fillchar to pass to ljust
        delimiter: delimiter between ljust'd strings
    Return: string of all ljust'd strings concatenated with the specified delimiter
    '''
    if type(width) == int:
        return delimiter.join([s.ljust(width, fillchar) for s in strs])
    else:
        assert len(strs) == len(width), "ljust_all: Length of `strs` and `width` must be the same"
        return delimiter.join([strs[i].ljust(width[i], fillchar) for i in range(len(strs))])