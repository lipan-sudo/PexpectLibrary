# Interact with the python's toplevel.
# Run this script with:
#   robot --rpa --console none python.robot
*** Settings ***
Library    PexpectLibrary

*** Tasks ***

Main
    Spawn    python    echo=FALSE
    Expect Exact    >>>${SPACE}
    Main Loop

*** Keywords ***

Main Loop
    ${query}    Set Variable    ${{ input('Your python expresion: ') }}
    Send Line   ${query}
    ${prompt}   Set Variable    >>>${SPACE}
    ${status}   Expect Exact    ${{ [ $prompt, pexpect.EOF ] }}

    # exit ?
    Run Keyword If    ${status} == 1
    ...    Run Keyword And Return    Wait

    ${before}   Before
    Log To Console    ${before}
    Run Keyword And Return    Main Loop
