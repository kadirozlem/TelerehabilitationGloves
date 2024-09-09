from dataclasses import dataclass
@dataclass
class Configuration:
    Save = True
    StartIndex = 0
    FullDataSize = 15000
    ResourceStartIndex = 10
    ResourceEndIndex = 310
    TestCount = 7
    ShowBoxPlot = True
    ShowBox = False
    ShowBar = True
    AttributeName = "Latency"
