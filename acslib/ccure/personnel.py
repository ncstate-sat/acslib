from acslib.ccure.base import CcureACS


class Personnel(CcureACS):
    def __init__(self):
        super().__init__()
        self.personnel = None
