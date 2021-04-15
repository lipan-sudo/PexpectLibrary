*** Settings ***
Library    PexpectLibrary
Library    String

*** Tasks ***
Main
    Spawn    uptime
    Expect    up\\s+(.*?),\\s+([0-9]+) users?,\\s+load averages?: ([0-9]+\\.[0-9][0-9]),?\\s+([0-9]+\\.[0-9][0-9]),?\\s+([0-9]+\\.[0-9][0-9])
    ${duration}    ${users}    ${av1}    ${av5}    ${av15}    Match Groups

    ${days}    ${hours}    ${mins}    Set Variable    0    0    0
    ${days}    Parse Days    ${duration}    ${days}
    ${hours}    ${mins}    Parse Hours And Minutes    ${duration}    ${hours}    ${mins}

    Log To Console    days, hours, minutes, users, cpu avg 1 min, cpu avg 5 min, cpu avg 15 min
    Log To Console    ${days}, ${hours}, ${mins}, ${users}, ${av1}, ${av5}, ${av15}

*** Keywords ***

Parse Days
    [Arguments]    ${duration}    ${default}
    ${m}    Get Regexp Matches    ${duration}    ([0-9]+)\\s+day    1    
    Return From Keyword If    ${{ len($m) < 1 }}    ${default}
    Return From Keyword    ${m}[0]

Parse Hours And Minutes
    [Arguments]    ${duration}    ${default_hours}    ${default_mins}
    ${m}    Get Regexp Matches    ${duration}    ([0-9]+):([0-9]+)    1    2
    Return From Keyword If    ${{ len($m) > 0 }}    ${m}[0]
    ${m}    Get Regexp Matches    ${duration}    ([0-9]+)\\s+min    1
    Return From Keyword If    ${{ len($m) > 0 }}    ${default_hours}    ${m}[0]
    Return From Keyword    ${default_hours}    ${default_mins}

