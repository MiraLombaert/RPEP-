#0.1: import necessary modules: 
import numpy, pandas, os, time, random
from psychopy import visual, gui, core, event, data

#0.2: choose directory to write to, if not yet existing, create it 
directory_to_write_data = os.path.join(os.getcwd(), "RPEPdatafiles")

if not os.path.isdir(directory_to_write_data): #if the directory does not exist yet, make it now
    os.mkdir(directory_to_write_data)
    
#1. dialog box: ask the demographics questions and make a file: 
   
already_exists = True
while already_exists: 
    dialogquestions     = {
    "Name": "Fill in your first name.",
    "Number": 0, "Age": 18,
    "Gender": ["Female", "Male", "Other"],
    "Handedness": ["Left", "Right", "Ambidextrous"]
    }
    dialog              = gui.DlgFromDict(dictionary= dialogquestions, title= "Participant Info: ")
    
    participant_number      = dialogquestions["Number"]
    participant_age         = int(dialogquestions["Age"])
    participant_handedness  = dialogquestions["Handedness"]
    name                    = dialogquestions["Name"][0].upper() + dialogquestions["Name"][1:] #capitalize the name
    
    dialogquestions.pop("Name") #remove the participant name for anonimity
    
    file_name = os.path.join(directory_to_write_data, "RPEP_" + "ParticipantNr_" + str(participant_number))
    
    if not os.path.isfile(file_name): #if the file doesn't exist, make it
        already_exists = False
        
    else: #tell the participant what to do as the file name is already used
        myDlg = gui.Dlg(title = "Error")
        myDlg.addText("Try another participant number")
        myDlg.show()
        
#0.1: graphical elements and constant variables
    #constants
response_keys     = ["w", "o", "space", "escape"] 
fixation_duration = 0.5 #time for fixation point
stimulus_duration = 3 #time that they receive for product calculation
max_response_time = 2 
        #lists of all products: ever interval consists of two lists
            # list 1: the 'smaller' units digit
            # list 2: the 'bigger' units digit
first             = [["1 x 1", "1 x 2", "1 x 3", "1 x 4", "1 x 5", "2 x 2"],["1 x 6", "1 x 7", "1 x 8", "1 x 9", "1 x 10", "3 x 3", "2 x 3", "2 x 4", "2 x 5"]]
second            = [["2 x 6", "2 x 7", "3 x 4"], ["2 x 8", "2 x 9", "2 x 10", "3 x 6", "4 x 4", "4 x 5"]]
third             = [["3 x 7", "3 x 8", "4 x 6", "5 x 5"], ["3 x 9", "3 x 10", "4 x 7", "5 x 6"]]
forth             = [["4 x 8", "5 x 7"],["4 x 9", "4 x 10", "5 x 8", "6 x 6"]]
fifth             = [["5 x 9", "6 x 7"],["5 x 10", "6 x 8", "7 x 7"]]
sixth             = [["6 x 9"],["6 x 10", "7 x 8"]]
seventh           = [["7 x 9", "8 x 8"],["7 x 10"]]
eighth            = [["8 x 9"],["8 x 10"]]
ninth             = [["9 x 9"],["9 x 10"]]
tenth             = [["13 x 7"],["10 x 10"]] #laat deze weg

interval_dictionary = {0: first, 1: second, 2: third, 3: forth, 4: fifth, 5: sixth, 6:seventh, 7: eighth, 8:ninth, 9: tenth}

    #graphical elements
win                 = visual.Window(units= "norm", color= "black", fullscr= True)
text_message        = visual.TextStim(win, text="", alignText= 'center',wrapWidth= 2.0)
fixation_point      = visual.TextStim(win, text= ".", alignText= 'center', color= "white")
product_stim        = visual.TextStim(win, text= "", color= "white") #all products should be made with this
decision_display    = visual.TextStim(win, text= ".", color= "white") #all the elements of the decision display should be made with this
my_clock            = core.Clock()

#1: functions
def create_message(text = "", response_keys = "space", duration = None, height = None, pos = (0,0), color = "white"):
    text_message.text = text
    text_message.height = height
    text_message.pos = pos
    text_message.color = color
    text_message.draw()
    win.flip()
    
    if duration is None: 
        event.waitKeys(keyList= response_keys)
        return None
    else: 
        time.sleep(duration)
        return None
        
def pick_no_correct_answer_trials(): 
    """ 
    This function will when called pick 4 random trials and make sure that there is 
    no correct answer available to the multiplication stimulus when the decision display is portrayed. 
    
    The trials will be presented as follows and will be returned as a numpy matrix with 4 rows and 5 collumns: 
        [uniques(=range (80:84)), interval(random), unit(random), distractor(random), response (=2 = space)]
    """
    
    #make the numpys from which a random index will be selected
    interval, unit, distractor = numpy.arange(0, 10), numpy.arange(0, 2), numpy.arange(0, 2)
    
    x1      = [80, numpy.random.choice(interval), numpy.random.choice(unit), numpy.random.choice(distractor) ,2]
    x2      = [81, numpy.random.choice(interval), numpy.random.choice(unit), numpy.random.choice(distractor) ,2]
    x3      = [82, numpy.random.choice(interval), numpy.random.choice(unit), numpy.random.choice(distractor) ,2]
    x4      = [83, numpy.random.choice(interval), numpy.random.choice(unit), numpy.random.choice(distractor) ,2]

    return numpy.array([x1, x2, x3, x4])

def extract_the_numbers(product_string): #e.g: 2 x 3 as string -> 2 and 3 as strings in a list
    """
    This function will split the product string that is retrieved from the interval lists. 
    It will split it at the multiplication symbol 'x' and return the individual factors as a list. 
    """
    return product_string.split("x")
    
def select_products_from_interval(interval, side):
    """
    This function will select a product from the interval that was given as input to the function
    depending on the provided side of the interval (units digit <5, >5). It will return this product 
    but it will make sure that the factors are randomly ordered, with sometimes the big factor appearing
    on the left and sometimes the small factor. 
    """
    product_string = random.choice(interval[side])  # Select a random product string from the correct side
    product_numbers = extract_the_numbers(product_string)  # Extract numbers from the product string
    
    # Create product_list with both possible orderings of the numbers
    product_list = [
        f"{product_numbers[0]} x {product_numbers[1]}", 
        f"{product_numbers[1]} x {product_numbers[0]}"
    ]
    # Return a random product string from the list
    return random.choice(product_list)
    
def get_the_distractor(numbers, distractortype): #is the distractor bigger or smaller than the solution? 
    """
    This function will provide a distractor number that is one (smallest) factor
    bigger (distractortype = big) or smaller (distractortype = small) than the correct answer. 
    """
    number1, number2 = int(numbers[0]), int(numbers[1])
    number2 += 1 if distractortype == "big" else -1

    return str(number1 * number2)
    
def get_the_right_solution_and_distractor(product_string, distractortype, correctresponse): 
    """
    This function will provide the correct sollution and the correct distractor for 
    the decision display. 
    """
    numbers         = extract_the_numbers(product_string)
    distractor      = get_the_distractor(numbers, distractortype)
    solution        = str(int(numbers[0].strip())*int(numbers[1].strip()))
        
    if correctresponse == "space": # subtract 2 if it is a trial with no correct answer
        solution = str(int(solution) - 2)

    return str(solution), str(distractor)

def create_decision_display_text(solution, distractor, location_of_correct):
    """
    This function will provide you the string to create the decision display.
    """
    if location_of_correct == "w": #the location of the correct answer is on the left
        decision_display_string = solution + "                           " + distractor
    else: 
        decision_display_string = distractor + "                           " + solution
    
    return decision_display_string

#2: define levels of factors and amounts
    #levels of factors: 
interval_levels         = ["first","second", "third", "forth", "fifth", "sixth", "seventh", "eight", "ninth", "tenth"] 
unit_levels             = ["small", "big"] #the units digit can either be <= 5 or > 5
distractor_levels       = ["small", "big"] #the distractor will be big or small
correctresponse_levels  = ["w", "o"] #the correct response is either q = left, p = right

    #amount of levels: N of all factors, and of uniques
Ninterval           = len(interval_levels) #= 10
Nunit               = len(unit_levels) #= 2
Ndistractor         = len(distractor_levels) #= 2
Ncorrectresponse    = len(correctresponse_levels) #= 2
Nunique             = Ninterval * Nunit * Ndistractor * Ncorrectresponse #= 80

    #amount of phases, blocks, trials
Nphases                 = 2 #practice and experiment phase 
Nblocks_per_exp         = 5
Ntrials_per_block       = 80
Nreps_within_block      = int(Ntrials_per_block/Nunique) # = 1 
Ntrials_per_experiment  = Ntrials_per_block*Nblocks_per_exp # = 480

#3: create the design: which information needs to be stored in the matrix of the experimenttrials? 
    #make the unique trial matrix and also add the no correct answer trials
uniquetrialsarray       = (numpy.array(range(Nunique))).astype(int)
interval_array          = (numpy.floor(uniquetrialsarray/(Nunit*Ndistractor*Ncorrectresponse)) % Ninterval).astype(int) # 0 = interval 1, 1 = interval 2
unit_array              = (numpy.floor(uniquetrialsarray/(Ndistractor*Ncorrectresponse)) % Nunit).astype(int) #0= small, 1= big
distractor_array        = (numpy.floor(uniquetrialsarray/Ncorrectresponse) % Ndistractor).astype(int) #0= small, 1= big
correctresponse_array   = (numpy.floor(uniquetrialsarray/1) % Ncorrectresponse).astype(int) #0= "q", 1= "p"
uniquetrialsmatrix      = numpy.column_stack([uniquetrialsarray, interval_array, unit_array, distractor_array, correctresponse_array]) #matrix with unique trial types, first column contains numbers to indicate which type of trial it is
print(uniquetrialsmatrix)

    #make an unfilled matrix of the size of the actual experimental design matrix
blocktrials = numpy.tile(uniquetrialsmatrix, (Nreps_within_block, 1)) #matrix containing one block

Ncolumns_of_design = blocktrials.shape[1] #how many columns of information about the trials are there up till now? 
experimenttrials = numpy.ones((Ntrials_per_experiment + 4*Nblocks_per_exp, Ncolumns_of_design + 1)) * numpy.nan #matrix to be filled with the information about each trial

    #fill in the experimental design matrix and randomize per block, the same trial type can not be repeated immediately after each other: 
for block in range(Nblocks_per_exp): #now we need to fill in the full experimenttrials matrix and randomize it per block
    no_correct_answer_trials    = pick_no_correct_answer_trials()
    blocktrials_extended        = numpy.vstack((blocktrials, no_correct_answer_trials))
    repetition                  = True
    
    while repetition: #check if there is a repetitive trial somewhere
        
        #add to the blocktrials 4 rows of the no correct answer trials
        numpy.random.shuffle(blocktrials_extended) #randomize the trials per block
        
        # calculate the difference based on the trial type
        comparison = numpy.diff(blocktrials_extended[:, 0]) 
        
        # check whether there was a repetition
        if sum(comparison == 0) == 0:
            repetition = False

        #give every trial a number
        currenttrialindexing = (numpy.array(range   (  len(blocktrials_extended)  ))   +   (block * (len(blocktrials_extended))  )).astype(int)
        
        #add the randomized trials to the experimenttrials design
    experimenttrials[currenttrialindexing, 0 : Ncolumns_of_design] = blocktrials_extended #store the trials for this block in the full design
        
        # add the block number: 
    #experimenttrials[currenttrialindexing, Ncolumns_of_design] = int(block + 1) #fill in the block number starting from 1
        # add the trial number
    experimenttrials[currenttrialindexing, Ncolumns_of_design] = currenttrialindexing
    
print(experimenttrials)

#4:validation
    ## creating pandas dataframe from numpy array
experimenttrials_DF = pandas.DataFrame.from_records(experimenttrials)

    ##name the columns
experimenttrials_DF.columns = ["trialtype", "interval", "unit", "distractor_size", "correctresponse_location", "trial"]
    ##cross table validation: correctresponse as rows, interval as collumns, should be 2
print(pandas.crosstab(experimenttrials_DF.correctresponse_location, experimenttrials_DF.interval))

#5: the main experiment: 

        # phase introduction
phase_text_practice = ("Je begint nu aan de oefenfase.\n\n Druk op 'spatie' om door te gaan.")
phase_text_experiment = (f"Je begint nu aan de testfase.\n\n De komende fase bestaat uit {str(Nblocks_per_exp)} blokken met pauzes tussendoor.\n")

instruction_text_1 = (
    "Tijdens deze taak worden eenvoudige vermenigvuldigings-\n"
    "oefeningen op het scherm getoond. Alle oefeningen resulteren\n"
    "in getallen tussen 1 en 100. We vragen je om deze oefeningen\n"
    "zo snel en nauwkeurig mogelijk op te lossen.\n\n"
    "Druk op 'spatie' om door te gaan."
)


instruction_text_2 = (
    "Kort na het tonen van de vermenigvuldigingsopgave zal er\n"
    "een scherm verschijnen met twee getallen. Eén daarvan zal\n"
    "de juiste oplossing zijn van de eerder opgeloste opgave.\n"
    "We vragen je om zo snel mogelijk de juiste oplossing te\n"
    "kiezen door op ‘w’ (links) of ‘o’ (rechts) te drukken. Na\n"
    "twee seconden verdwijnt dit scherm weer. Gebruik je linker-\n"
    "en rechterwijsvinger om deze toetsen in te drukken.\n\n"
    "Druk op 'spatie' om door te gaan."
)


instruction_text_3 = (
    "Het is mogelijk dat de juiste oplossing niet wordt getoond\n"
    "op het beslissingsscherm. In dat geval vragen we je om op\n"
    "'spatie' te drukken. Gebruik beide duimen om de spatiebalk\n"
    "in te drukken. Houd je wijsvingers en duimen boven de juiste\n"
    "toetsen gedurende het hele experiment.\n\n"
    "Druk op 'spatie' om door te gaan."
)
    #create the lists of dictionaries, needed to pass to the experimenthandler
experimenttrial_list = pandas.DataFrame.to_dict(experimenttrials_DF, orient = "records") #convert the pandas dataframe to a list of dictionaries
this_exp = data.ExperimentHandler(dataFileName = file_name, extraInfo = dialogquestions)

    #welcome + instructions
create_message(text=f"Welkom {name}!\n\n Druk op 'spatie' om verder te gaan.") 
create_message(text= instruction_text_1)
create_message(text= instruction_text_2)
create_message(text= instruction_text_3)

for b in range(Nblocks_per_exp + 1): #select the current block of the experiment, the first block (== 0) is the practice phase
    #pick the trials for this block from the experimenttrials and couple the trial handler
    #and the experiment handler to each other
        
    if b == 0: #it's the practice phase
        create_message(text= phase_text_practice)
        trials = data.TrialHandler(trialList= experimenttrial_list[40:50], nReps= 1, method= 'random') 
        this_exp.addLoop(trials) #couple the trial handler and the experiment handler to each other
    
    else: #it's the experiment phase
        if b == 1: #introduce experiment phase
            create_message(text= phase_text_experiment)
        
        create_message(text=f"Dit is blok {str(b)} van {str(Nblocks_per_exp)}.\n Druk op 'spatie' als je klaar bent om te beginnen.")
        trials= data.TrialHandler(trialList= experimenttrial_list[(b-1)*Ntrials_per_block: (b-1)*Ntrials_per_block + Ntrials_per_block], nReps = 1, method= 'sequential')
        this_exp.addLoop(trials) #couple the trial handler and the experiment handler to each other

    for t in trials: #select the current trial of the current block
        #extract all relevant information for the task from the t-dictionary 
        interval                             = int(t["interval"])
        unit                                 = int(t["unit"])
        distractor_size                      = distractor_levels[int(t["distractor_size"])]
        correctresponse                      = response_keys[int(t["correctresponse_location"])] 
        current_product                      = select_products_from_interval(interval_dictionary[interval], unit)

        #extract from the given information the correct solution and distractor
        current_solution, current_distractor = get_the_right_solution_and_distractor(current_product, distractor_size, correctresponse)
        
        #show fixation point
        fixation_point.draw()
        win.flip()
        time.sleep(fixation_duration)
        
        #display product
        product_stim.text = current_product
        product_stim.draw()
        win.flip()
        time.sleep(stimulus_duration)
        
        #show fixation point
        fixation_point.draw()
        win.flip()
        time.sleep(fixation_duration)
        
        #display decision display
        decision_display.text = create_decision_display_text(current_solution, current_distractor, correctresponse)
        decision_display.draw()
        win.flip()
        event.clearEvents(eventType = "keyboard")
        my_clock.reset()
        
        response        = event.waitKeys(keyList= response_keys, maxWait= max_response_time)
        RT              = my_clock.getTime()
        
        if response is None: 
            response = "N" #N means no response was given
            accuracy = 0 
        
        elif response[0] == "escape": 
            break
            
        else:
            accuracy = int(response[0] == correctresponse)
        
        
        if b == 0: #if practice phase, give feedback
            if response == "N": 
                feedback_text = "Te traag!"
            elif accuracy == 0: 
                feedback_text = "Incorrect!"
            else: 
                feedback_text = "Correct!"
                
            create_message(text= feedback_text, duration = 1)
        
        #store: experiment phase(practice phase or actual experiment?), given response, accuracy, response time 
        trials.addData("givenresponse", response[0]) 
        trials.addData("correctresponse", correctresponse)
        trials.addData("Accuracy", int(accuracy)) # 0 for incorrect or too slow, 1 for correct
        trials.addData("RT", RT) 
        trials.addData("product", current_product)
        trials.addData("solution", int(current_solution))
        trials.addData("distractor", int(current_distractor))
        trials.addData("Phase of Exp", 0 if b == 0 else 1) #this is for when I have added the practice trials
        trials.addData("Block", b)
        this_exp.nextEntry()
        
    if response[0] == "escape": 
                    break
    
create_message(text=f"Dit is het einde van het experiment.\n Dankjewel {name} voor je deelname!")
this_exp.close()
win.close()
    

    



