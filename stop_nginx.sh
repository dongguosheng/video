ps aux | grep [n]ginx | awk '{print $2}' | xargs kill -9
