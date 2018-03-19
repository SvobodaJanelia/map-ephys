import datajoint as dj
import lab, ccf

schema = dj.schema(dj.config['experiment.database'])

@schema
class Task(dj.Lookup):
    definition = """
    # Type of tasks
    task            : varchar(12)                  # task type
    ----
    task_description : varchar(4000)
    """
    contents = [
         ('audio delay', 'auditory delayed response task (2AFC)'),
         ('audio mem', 'auditory working memory task'),
         ('s1 stim', 'S1 photostimulation task (2AFC)')
         ]

@schema
class Session(dj.Manual):
    definition = """
    -> lab.Subject
    session : smallint 		# session number
    ---
    session_date  : date
    -> lab.Person
    -> lab.Rig
    """
    
    class Trial(dj.Part):
        definition = """
        -> Session
        trial   : smallint
        ---
        start_time : decimal(8,4)  # (s)
        end_time : decimal(8,4)  # (s)
        """

@schema 
class TrialNoteType(dj.Lookup):
    definition = """
    trial_note_type : varchar(12)
    """
    contents = zip(('autolearn', 'protocol #', 'bad', 'bitcode'))

@schema
class TrialNote(dj.Manual):
    definition = """
    -> Session.Trial
    -> TrialNoteType
    ---
    trial_note  : varchar(255) 
    """

@schema
class TrainingType(dj.Lookup):
    definition = """
    # Mouse training
    training_type : varchar(100) # mouse training
    ---
    training_type_description : varchar(2000) # description
    """
    contents = [
         ('regular', ''),
         ('regular + distractor', 'mice were first trained on the regular S1 photostimulation task  without distractors, then the training continued in the presence of distractors'),
         ('regular or regular + distractor', 'includes both training options')
         ]
    
@schema
class SessionTraining(dj.Manual):
    definition = """
    -> Session
    -> TrainingType
    """

@schema
class TrialEventType(dj.Lookup):
    definition = """
    trial_event_type  : varchar(12)  
    """
    contents = zip(('delay', 'go', 'sample', 'presample'))

@schema
class Outcome(dj.Lookup):
    definition = """
    outcome : varchar(32)
    """
    contents = zip(('hit', 'miss', 'ignore'))

@schema 
class EarlyLick(dj.Lookup):
    definition = """
    early_lick  :  varchar(32)
    """ 
    contents = zip(('early', 'no early'))

     
@schema 
class TrialInstruction(dj.Lookup):
    definition = """
    # Instruction to mouse 
    trial_instruction  : varchar(8) 
    """
    contents = zip(('left', 'right'))

@schema
class BehaviorTrial(dj.Manual):
    definition = """
    -> Session.Trial
    ----
    -> Task
    -> TrialInstruction
    -> EarlyLick
    -> Outcome
    """

@schema
class TrialEvent(dj.Manual):
    definition = """
    -> BehaviorTrial 
    -> TrialEventType
    trial_event_time : decimal(8, 4)   # (s) from trial start, not session start
    ---
    duration : decimal(8,4)  #  (s)  
    """

@schema
class ActionEventType(dj.Lookup):
    definition = """
    action_event_type : varchar(32)
    ----
    action_event_description : varchar(1000)
    """
    contents =[  
       ('left lick', ''), 
       ('right lick', '')]

@schema
class ActionEvent(dj.Manual):
    definition = """
    -> BehaviorTrial
    -> ActionEventType
    action_event_time : decimal(8,4)  # (s) from trial start
    """

@schema
class TrackingDevice(dj.Lookup):
    definition = """
    tracking_device  : varchar(8)  # e.g. camera, microphone
    ---
    sampling_rate  :  decimal(8, 4)   # Hz
    tracking_device_description: varchar(255) # 
    """

@schema
class Tracking(dj.Imported):
    definition = """
    -> Session.Trial 
    -> TrackingDevice
    ---
    tracking_data_path  : varchar(255)
    start_time : decimal(8,4) # (s) from trial star
    """

@schema
class PhotostimDevice(dj.Lookup):
    definition = """
    photostim_device  : varchar(20)
    ---
    excitation_wavelength :  decimal(5,1)  # (nm) 
    photostim_device_description : varchar(255)
    """

@schema 
class Photostim(dj.Manual):
    definition = """
    -> PhotostimDevice
    photo_stim :  smallint 
    ---
    -> ccf.CCF
    duration  :  decimal(8,4)   # (s)
    waveform  :  longblob       # (mW)
    """

    class Profile(dj.Part):
        definition = """
        -> master
        (profile_x, profile_y, profile_z) -> ccf.CCF(x, y, z)
        ---
        intensity_timecourse   :  longblob  # (mW/mm^2)
        """

@schema
class PhotostimTrial(dj.Imported):
    definition = """
    -> Session.Trial
    """

    class Event(dj.Part):
        definition = """
        -> master
        -> Photostim
        photostim_event_time : decimal(8,3)   # (s) from trial or session start or whatever 
        """

@schema
class PassivePhotostimTrial(dj.Computed):
    definition = """
    -> PhotostimTrial
    """
    key_source = PhotostimTrial() - BehaviorTrial()

    def make(self, key):
        self.insert1(key)

@schema
class TaskProtocol(dj.Lookup):
    definition = """
    # SessionType
    -> Task
    task_protocol : tinyint # task protocol
    ---
    task_protocol_description : varchar(4000)
    """
    contents = [
         ('s1 stim', 2, 'mini-distractors'),
         ('s1 stim', 3, 'full distractors, with 2 distractors (at different times) on some of the left trials'),
         ('s1 stim', 4, 'full distractors'),
         ('s1 stim', 5, 'mini-distractors, with different levels of the mini-stim during sample period'),
         ('s1 stim', 6, 'full distractors; same as protocol 4 but with a no-chirp trial-type'),
         ('s1 stim', 7, 'mini-distractors and full distractors (only at late delay)'),
         ('s1 stim', 8, 'mini-distractors and full distractors (only at late delay), with different levels of the mini-stim and the full-stim during sample                 period'),
         ('s1 stim', 9, 'mini-distractors and full distractors (only at late delay), with different levels of the mini-stim and the full-stim during sample period')
         ]
        
@schema
class SessionTask(dj.Manual):
    definition = """
    -> Session
    -> TaskProtocol
    """