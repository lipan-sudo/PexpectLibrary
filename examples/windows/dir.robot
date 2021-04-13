*** Settings ***
Library    PexpectLibrary

*** Tasks ***

Main   
    Popen Spawn    cmd.exe /q    cwd=C:\\    
    Expect Exact    C:\\>
    Send Line    chcp 65001
    Expect Exact    C:\\>
    Send Line    dir
    Expect Exact    C:\\>
    ${data}    Before
    Log To Console    ${data}
    Kill 
    Wait