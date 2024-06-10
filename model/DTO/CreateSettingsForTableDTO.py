class CreateSettingsForTableDTO:
    def __init__(self):
        self.agency = None
        self.route = None
        self.weekday = None
        self.dates = None
        self.direction = None
        self.individual_sorting = False
        self.timeformat = 1
        self.create_plan_mode = None
        self.output_path = ""
