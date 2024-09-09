from dataclasses import dataclass


@dataclass(frozen=True)
class FileOperation:
    WritePeriod = 5
    FileDirectory = "./testresult/"
    TestName = "TestSubject12"

@dataclass(frozen=True)
class Window:
    refresh_count = 5
    columncount = 5
    width = 1694
    height = 895
    padding = 20
    small_padding = 8
    info_box_height = 80
    info_box_label_height = 25
    button_width = 180
    button_height = 25
    btn_padding = 10
    four_button_width=130
    five_button_width=100
    move_buttons_width=80
    new_line_padding=40


class Configuration:
    RandomState = 17
    Data ='./Data_Orj/'
    PreprocessedData = './PreprocessedData/'
    Model = './Model/'
    Results  = './Results/'
    TestName = 'TSFEL/'
    SN_Cal_Start =50
    SN_Cal_End = 550
    SN_MinArrSize = 200
    Sample_Distance = 19
    Frequency = 50
    TrainRatio = 0.75
    OnlyMoveFingers=True
    ReloadPreprocessed = True
    BufferCount = 20
    FeatureCount = 23