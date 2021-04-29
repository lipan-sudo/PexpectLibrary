# Interact with the swi-prolog's toplevel. It's a little gift for xiaohei ;-)
# Run this script with:
#   robot --rpa --console none swipl.robot
*** Settings ***
Library    PexpectLibrary

*** Tasks ***

Main
    Spawn    /usr/bin/swipl    [ '--quiet', '-tty', '-g', 'set_prolog_flag(color_term, false).' ]    echo=FALSE
    Expect Exact    1 ?-
    Main Loop    2

*** Keywords ***

Main Loop
    [Arguments]    ${counter}
    ${query}    Set Variable    ${{ input('Your prolog query: ') }}
    Send Line   ${query}
    ${regexp}   Set Variable    ${counter} \\?-${SPACE}
    ${status}   Expect    ${{ [ $regexp, pexpect.EOF ] }}

    # exit ?
    Run Keyword If    ${status} == 1
    ...    Run Keyword And Return    Wait

    ${before}   Before
    ${counter}  Evaluate    ${counter}+1
    Log To Console    ${before}
    Main Loop    ${counter}
