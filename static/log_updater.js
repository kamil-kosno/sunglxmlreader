setInterval(updateLog, 30000)
function updateLog(){
    fetch('/update_log')      
}
updateLog()