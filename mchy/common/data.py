
def _get_version_int():
    from mchy.common._raw_data import VERSION_STR

    def get_nth_element(arr, n):
        if n < len(arr):
            return arr[n]
        else:
            return 0

    nums = tuple(map(int, VERSION_STR.lstrip("v").split("-")[0].split(".")))
    return sum([
        (100**3)*get_nth_element(nums, 0),
        (100**2)*get_nth_element(nums, 1),
        (100**1)*get_nth_element(nums, 2),
        (100**0)*get_nth_element(nums, 3)
    ])


VERSION_INT = _get_version_int()
