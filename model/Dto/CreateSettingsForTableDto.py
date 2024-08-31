from model.Enum.GTFSEnums import CreatePlanMode


class CreateSettingsForTableDTO:
    def __init__(self):
        self.agency = None
        self.route = None
        self.weekday = None
        self.dates = None
        self.direction = 0
        self.individual_sorting = False
        self.timeformat = 1
        self.create_plan_mode = CreatePlanMode.date
        self.output_path = ""
