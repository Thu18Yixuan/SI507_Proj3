#################################
##### Name: Yixuan Jia ##########
##### Uniqname: jiayx ###########
##### UMID: 46990186 ############
#################################
import sqlite3
import plotly.graph_objs as go

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()

# Part 1: Implement logic to process user commands
def process_command(command):
    if check_if_command_is_valid(command):
        command_content_list = command.split()
        if command_content_list[0] == 'bars':
            process_command_bar(command_content_list)
        elif command_content_list[0] == 'companies':
            process_command_company(command_content_list)
        elif command_content_list[0] == 'countries':
            process_command_country(command_content_list)
        elif command_content_list[0] == 'regions':
            process_command_region(command_content_list)
        else:
            process_command_bar(command_content_list)
    else:
        print('Command not recognized: ' + command)

def process_command_bar(command_content_list):
    # Initialize option parameter
    option_country = None
    option_region = None
    option_sell_or_source = 'sell'
    option_sorting = 'Rating'
    option_sorting_order = 'DESC'
    option_limit = 10
    option_barplot = False

    # Set option parameter for country and region
    for content in command_content_list:
        if 'country' in content:
            option_country = content.split('=')[1]
            break
        elif 'region' in content:
            option_region = content.split('=')[1]
            break
        else:
            continue
    
    # Set option parameter for sell_or_source
    if 'source' in command_content_list:
        option_sell_or_source = 'source'
    
    # Summarize option parameter above for sql query
    option_country_seller = '\'%\''
    option_region_seller = '\'%\''
    option_country_source = '\'%\''
    option_region_source = '\'%\''
    if option_country and option_sell_or_source == 'sell':
        option_country_seller = '\'' + option_country + '\''
    if option_region and option_sell_or_source == 'sell':
        option_region_seller = '\'' + option_region + '\''
    if option_country and option_sell_or_source == 'source':
        option_country_source = '\'' + option_country + '\''
    if option_region and option_sell_or_source == 'source':
        option_region_source = '\'' + option_region + '\''
    
    # Set option parameter for sorting accordance
    if 'cocoa' in command_content_list:
        option_sorting = 'CocoaPercent'
    
    # Set option parameter for sorting order
    if 'bottom' in command_content_list:
        option_sorting_order = 'ASC'
    
    # Set option parameter for limit number
    try:
        if command_content_list[-1].isnumeric():
            option_limit = int(command_content_list[-1])
    except:
        pass

    try:
        if command_content_list[-2].isnumeric():
            option_limit = int(command_content_list[-2])
    except:
        pass

    # Set option parameter for barplot
    if 'barplot' in command_content_list:
        option_barplot = True
    
    # Write SQL query
    sql_query_bars_template = '''
        SELECT Bars.SpecificBeanBarName, Bars.Company, C1.EnglishName, Bars.Rating, Bars.CocoaPercent, C2.EnglishName
        From Bars, Countries C1, Countries C2
        WHERE Bars.CompanyLocationId = C1.Id
        AND Bars.BroadBeanOriginId = C2.Id
        AND C1.Alpha2 like {}
        AND C1.Region like {}
        AND C2.Alpha2 like {}
        AND C2.Region like {}
        ORDER BY {} {}
        LIMIT {}
    '''
    sql_query_bars = sql_query_bars_template.format(
        option_country_seller, 
        option_region_seller, 
        option_country_source, 
        option_region_source,
        option_sorting,
        option_sorting_order,
        option_limit)
    result_list = cur.execute(sql_query_bars).fetchall()

    # Determine the display method
    if option_barplot:
        result_x_axis = []
        result_y_axis = []
        if option_sorting == 'CocoaPercent':
            for result in result_list:
                result_x_axis.append(result[0])
                result_y_axis.append(result[4])
        else: # option_sorting = 'Rating'
            for result in result_list:
                result_x_axis.append(result[0])
                result_y_axis.append(result[3])
        barplot_display(result_x_axis, result_y_axis)
    else:
        print_format(result_list)
    
def process_command_company(command_content_list):
    # Initialize option parameter
    option_country = '\'%\''
    option_region = '\'%\''
    option_aggregation = None
    option_sorting = None
    option_sorting_order = 'DESC'
    option_limit = 10
    option_barplot = False

    # Set option parameter for country and region
    for content in command_content_list:
        if 'country' in content:
            option_country = '\'' + content.split('=')[1] + '\''
            option_region = '\'%\''
            break
        elif 'region' in content:
            option_country = '\'%\''
            option_region = '\'' + content.split('=')[1] + '\''
            break
        else:
            continue
    
    # Set option parameter for aggregation
    if 'cocoa' in command_content_list:
        option_aggregation = 'Avg(CocoaPercent)'
    elif 'number_of_bars' in command_content_list:
        option_aggregation = 'COUNT(*)'
    else:
        option_aggregation = 'Avg(Rating)'
    
    # Set option parameter for sorting
    option_sorting = option_aggregation
    
    # Set option parameter for sorting order
    if 'bottom' in command_content_list:
        option_sorting_order = 'ASC'
    
    # Set option parameter for limit number
    try:
        if command_content_list[-1].isnumeric():
            option_limit = int(command_content_list[-1])
    except:
        pass

    try:
        if command_content_list[-2].isnumeric():
            option_limit = int(command_content_list[-2])
    except:
        pass

    # Set option parameter for barplot
    if 'barplot' in command_content_list:
        option_barplot = True
    
    # Write SQL query
    sql_query_companies_template = '''
        SELECT Bars.Company, Countries.EnglishName, {}
        From Bars, Countries
        WHERE Bars.CompanyLocationId = Countries.Id
        AND Countries.Alpha2 like {}
        AND Countries.Region like {}
        GROUP BY Bars.Company
        HAVING COUNT(*) > 4
        ORDER BY {} {}
        LIMIT {}
    '''
    sql_query_companies = sql_query_companies_template.format(
        option_aggregation,  
        option_country,
        option_region,
        option_sorting,
        option_sorting_order,
        option_limit)
    result_list = cur.execute(sql_query_companies).fetchall()
    
    # Determine the display method
    if option_barplot:
        result_x_axis = []
        result_y_axis = []
        for result in result_list:
            result_x_axis.append(result[0])
            result_y_axis.append(result[2])
        barplot_display(result_x_axis, result_y_axis)
    else:
        print_format(result_list)

def process_command_country(command_content_list):
    # Initialize option parameter
    option_region = '\'%\''
    option_sell_or_source = 'CompanyLocationId'
    option_aggregation = None
    option_sorting = None
    option_sorting_order = 'DESC'
    option_limit = 10
    option_barplot = False

    # Set option parameter for region
    for content in command_content_list:
        if 'region' in content:
            option_region = '\'' + content.split('=')[1] + '\''
            break
    
    # Set option parameter for sell_or_source
    if 'source' in  command_content_list:
        option_sell_or_source = 'BroadBeanOriginId'
    
    # Set option parameter for aggregation
    if 'cocoa' in command_content_list:
        option_aggregation = 'Avg(CocoaPercent)'
    elif 'number_of_bars' in command_content_list:
        option_aggregation = 'COUNT(*)'
    else:
        option_aggregation = 'Avg(Rating)'

    # Set option parameter for sorting
    option_sorting = option_aggregation
    
    # Set option parameter for sorting order
    if 'bottom' in command_content_list:
        option_sorting_order = 'ASC'
    
    # Set option parameter for limit number
    try:
        if command_content_list[-1].isnumeric():
            option_limit = int(command_content_list[-1])
    except:
        pass

    try:
        if command_content_list[-2].isnumeric():
            option_limit = int(command_content_list[-2])
    except:
        pass
    
    # Set option parameter for barplot
    if 'barplot' in command_content_list:
        option_barplot = True

    # Write SQL query
    sql_query_countries_template = '''
        SELECT Countries.EnglishName, Countries.Region, {}
        From Bars, Countries
        WHERE Bars.{} = Countries.Id
        AND Countries.Region like {}
        GROUP BY Countries.EnglishName
        HAVING COUNT(*) > 4
        ORDER BY {} {}
        LIMIT {}
    '''
    sql_query_countries = sql_query_countries_template.format(
        option_aggregation,
        option_sell_or_source,
        option_region,
        option_sorting,
        option_sorting_order,
        option_limit)
    result_list = cur.execute(sql_query_countries).fetchall()

    # Determine the display method
    if option_barplot:
        result_x_axis = []
        result_y_axis = []
        for result in result_list:
            result_x_axis.append(result[0])
            result_y_axis.append(result[2])
        barplot_display(result_x_axis, result_y_axis)
    else:
        print_format(result_list)

def process_command_region(command_content_list):
    # Initialize option parameter
    option_sell_or_source = 'CompanyLocationId'
    option_aggregation = None
    option_sorting = None
    option_sorting_order = 'DESC'
    option_limit = 10
    option_barplot = False

    # Set option parameter for sell_or_source
    if 'source' in command_content_list:
        option_sell_or_source = 'BroadBeanOriginId'

    # set option parameter for aggregation
    if 'cocoa' in command_content_list:
        option_aggregation = 'Avg(CocoaPercent)'
    elif 'number_of_bars' in command_content_list:
        option_aggregation = 'COUNT(*)'
    else:
        option_aggregation = 'Avg(Rating)'

    # Set option parameter for sorting
    option_sorting = option_aggregation

    # Set option parameter for sorting order
    if 'bottom' in command_content_list:
        option_sorting_order = 'ASC'
    
    # Set option parameter for limit number
    try:
        if command_content_list[-1].isnumeric():
            option_limit = int(command_content_list[-1])
    except:
        pass

    try:
        if command_content_list[-2].isnumeric():
            option_limit = int(command_content_list[-2])
    except:
        pass

    # Set option parameter for barplot
    if 'barplot' in command_content_list:
        option_barplot = True
    
    # Write SQL query
    sql_query_regions_template = '''
        SELECT Region, {}
        FROM Bars, Countries
        WHERE Bars.{} = Countries.Id
        GROUP BY Region
        HAVING COUNT(*) > 4
        ORDER BY {} {}
        LIMIT {}
    '''
    sql_query_regions = sql_query_regions_template.format(
        option_aggregation,
        option_sell_or_source,
        option_sorting,
        option_sorting_order,
        option_limit)
    result_list = cur.execute(sql_query_regions).fetchall()
    
    # Determine the display method
    if option_barplot:
        result_x_axis = []
        result_y_axis = []
        for result in result_list:
            result_x_axis.append(result[0])
            result_y_axis.append(result[1])
        barplot_display(result_x_axis, result_y_axis)
    else:
        print_format(result_list)    

def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

def print_format(results_list):
    '''Print out the results list in a certain format according to the data type

    Parameters
    ----------
    results_list: list
        A list of results fetched from database

    Returns
    -------
    None
    '''
    for results in results_list:
        for column_num in range(len(results)):
            # if the output is an integer
            if str(results[column_num]).isnumeric():
                print("{result:<5}".format(result = results[column_num]), end = '')
                continue

            # if the output is a number but not an integer
            if str(results[column_num])[0].isnumeric():
                if str(results[column_num])[0] != '0':
                    result = format(results[column_num], '<6.1f')
                    print(result, end = '')
                    continue
                else: # if the output is a percentage
                    result = str(format(results[column_num]*100, '0.0f')) + '%'
                    print("{result:<6}".format(result = result), end = '')
                    continue

            if len(str(results[column_num])) <= 12:
                print("{str:16}".format(str = str(results[column_num])), end = '')
            else:
                print(str(results[column_num])[0:12]+'... ', end = '')
        print()

def set_up_valid_input_words_list():
    '''Set up a list which contains all possibe valid input words

    Parameters
    ----------
    None

    Returns
    -------
    valid_input_words: list
        a list of valid input words
    '''
    valid_input_words = []

    # Append words from Countries.Alpha2
    sql_query_alpha2_words = '''
        SELECT Countries.Alpha2
        From Countries
    '''
    response_alpha2 = cur.execute(sql_query_alpha2_words).fetchall()
    for response in response_alpha2: 
        if len(response) != 0: # delete the blank item
            valid_input_words.append(response[0])

    # Append words from Countries.Region
    sql_query_region_words = '''
        SELECT Countries.Region
        From Countries
        GROUP BY Region
    '''
    response_region = cur.execute(sql_query_region_words).fetchall()
    for response in response_region:
        if len(response[0]) != 0:
            valid_input_words.append(response[0])

    # Append commands, options, and numbers
    command_words = ['bars', 'companies', 'countries', 'regions']
    option_words = ['none', 'country', 'region', 'sell', 'source', 'ratings', 'cocoa', 'number_of_bars', 'top', 'bottom', 'barplot']
    number_words = []
    for num in range(100):
        number_words.append(str(num))
    
    valid_input_words = valid_input_words + command_words + option_words + number_words
    return valid_input_words

def check_if_command_is_valid(command):
    '''Check if the input command is valid

    Parameters
    ----------
    command: string
        The input string of command
    
    Returns
    -------
    check_validation: bool
        A bool determines if the input command is valid
    '''
    check_validation = True

    # Set up a list of command words
    command_words_list = command.split()
    for item in command_words_list:
        if '=' in item:
            command_words_list = command_words_list + item.split('=')
            command_words_list.remove(item)
    
    # check if words in command_words_list is in valid_input_words_list
    for word in command_words_list:
        if word in valid_input_words_list:
            pass
        else:
            check_validation = False
            break
    
    return check_validation

def barplot_display(x_axis, y_axis):
    '''Display the data with bar chart

    Parameter
    ---------
    x_axis: list
        a list of x-axis values
    
    y_axis: list
        a list of y-axis values
    
    Returns
    -------
    None
    '''
    bar_data = go.Bar(x = x_axis, y = y_axis)
    fig = go.Figure(data = bar_data)
    fig.show()


# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue

        if response == 'exit':
            print('bye')
            quit()
        
        if response == '':
            continue
        
        process_command(response)

        # add to every process command
        '''
        if 'barplot' in response:
            barplot_display(process_result)
        else:
            print_format(process_result)
        '''

# Make sure nothing runs or prints out when this file is run as a module/library
if __name__=="__main__":
    # Set up a list of possible valid input words
    valid_input_words_list = set_up_valid_input_words_list()
    interactive_prompt()
