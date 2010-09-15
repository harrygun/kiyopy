"""This parser is my system for reading input files to large programs.  The idea
is that the only argument for the program should always be the input file and
all the parameters are read from that file.  The input file will have plain
python syntax.  I've found this to have the best flexibility, avoiding the
need to have many versions of the same code.

This is purposely written as a set of functions rather than a class.  I can
think of no reason that you would want the parser to stick around after being
called and the output dictionaries are pretty self contained.

Revision History:
    August 2010 - Wrote initial code (fileparser and dictparser). --Kiyo Masui
"""

import custom_exceptions as ce

def parse(ini_data, params, return_undeclared=False, checking=11):
    """
    Parses a python file or dictionary that defines a dictionary of 
    parameters.
    
    This function accepts a filename and a dictionary of keys and pre typed
    values. It returns a dictionary of the same keys with values read from
    file.  It optionally performs typechecking.

    Arguments:
        ini_data: a string containing a python file name or a dictionary.  The
            file must contain a script (not function) that defines parameter
            values in the local namespace.  Alternatly, if ini is a
            dictionary, then parameters are read from the dictionary.
            Variables must have names and
            types corresponding to the params dictionary argument.
        params: a dictionary of keys and corrsponding to variable names to be
            read from file and values corresponding to defaults if the
            corresponding variable is not found in the file.
        return_undeclared: Bool default False.  Whethar to return a second
            dictionary of with variables found in the parameter file but not in
            the in params argument.
        checking: Perform various checks:
            1's digit: performe type checking on the values in the file and in
                passed params:
                    0 not at all
                    1 print warning (default)
                    2 (or greater) raise an Exception
            10s digit: parameter feedback
                    0 none
                    1 print message when parameters remain default value
                    2 print all parameters and whethar they've defaulted

    Returns:
        out_params: A dictionary with the same keys as argument params but 
            with values read from file.
        undeclared: Optional. A dictionary that holds any key found in the 
            file but not in params. Returned if return_undeclared=True.
    """
    parcheck = (checking - checking%10)//10
    if isinstance(ini_data, str) :
        if parcheck > 0 :
            print 'Reading parameters from file: '+ ini_data
        # Convert local variables defined in python script to dictionary.
        # This is in a separate function to avoid namespace issues.
        dict_to_parse = _execute_parameter_file(ini_data)
    elif isinstance(ini_data, dict) :
        if parcheck > 0 :
            print 'Reading parameters from dictionary.'
        dict_to_parse = ini_data
    elif ini_data is None :
        if parcheck > 0 :
            print 'No input, all parameters defaulted.'
        if return_undeclared :
            return params, {}
        else :
            return params
    else :
        raise TypeError("Argument ini must be a dictionary, file name, "
                        "or None (to accept defaults).")
    
    return parse_dict(dict_to_parse, params, return_undeclared, checking)


def parse_dict(dict_to_parse, params, return_undeclared=False, checking=11):
    """
    Same as parse_ini.parse except parameters read from only dictionary.
    
    This function accepts an input dictionary and a dictionary of keys 
    and pre typed
    values. It returns a dictionary of the same keys with values read from
    the input dictionary.  See the docstring for pars for more
    information, the only difference is the argument ini replaces fname.

    Arguments:
        dict_to_parse: A dictionary containing keys and values to be read as
            parameters.  Entries should have keys and
            types corresponding to the pars dictionary argument (depending on
            level of checking requested).
      """
    
    # Separate the variouse checks in the checking argument.
    # For checking that the parsed type is the same as the declared params type
    typecheck = checking%10
    # Level of reporting for what happes to each parameter.
    parcheck = (checking - typecheck)//10
    # Same keys as params but for checking but contains only a flag to indicate
    # if parameter retained it's default value.
    defaulted_params = {}
    for key in params.iterkeys():
        defaulted_params[key] = True
    # Make dictionaries for outputs
    undeclared = {} # For keys found in dict_to_parse and not in params
    out_params = dict(params)

    # Loop over both input dictionaries and look for matching keys
    for inkey, invalue in dict_to_parse.iteritems():
        found_match_flag = False
        for key, value in params.iteritems():
            # Check for matching keys. Note stripping.
            if key.strip() == inkey.strip():
                if typecheck > 0:
                    if type(value)!=type(invalue):
                        if typecheck > 1:
                            raise ce.FileParameterTypeError(
                                "Tried to assign an input "
                                "parameter to the value of the wrong type " 
                                "and asked for strict type checking. "
                                "Parameter name: " + key)
                        else:
                            print ("Warning: Assigned an input "
                                "parameter to the value of the wrong type. "
                                "Parameter name: " + key)
                out_params[key] = invalue
                found_match_flag = True
                defaulted_params[key]=False
                # There shouldn't be another matching key so:
                break
        if not found_match_flag :
            # Value found in dict_to_parse was not found in params
            undeclared[inkey]=invalue
    # Check if parameters have remained a default value and print information
    # about the parameters that were set. Depending on feedback level.
    if parcheck > 0 :
        print "Parameters set."
        for key, value in out_params.iteritems():
            if defaulted_params[key] :
                print "parameter: "+key+" defaulted to value: "+str(value)
            elif parcheck > 1 :
                print "parameter: "+key+" obtained value: "+str(value)

    if return_undeclared :
        return out_params, undeclared
    else :
        return out_params

    

def _execute_parameter_file(this_parameter_file_name):
    """
    Executes python script in named file and returns dictionary of variables
    declared in that file.
    """
    
    # Only a few locally defined variables and all have a long name to avoid
    # namespace conflicts.

    # Execute the filename which presumably holds a python script. This will
    # bring the parameters defined there into the local scope.
    exec(open(this_parameter_file_name).read())
    # Store the local scope as a dictionary.
    out = locals()
    # Delete all entries of out that correspond to variables defined in this
    # function (i.e. not in the read file).
    del out['this_parameter_file_name']
    # Return the dictionary of parameters read from file.
    return out