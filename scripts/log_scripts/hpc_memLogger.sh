printf "%-8s %-15s %-10s %-10s %-15s %-15s %-15s %-s\n" "PID" "USER" "%CPU" "%MEM" "RSS (MB)" "VSZ (MB)" "VmPeak (MB)" "COMMAND"

# Get top 24 processes sorted by %MEM
ps -eo pid,user,%cpu,%mem,rss,vsize,comm --sort=-%cpu | head -n 25 | tail -n 24 | while read -r pid user cpu mem rss vsz comm; do
    mem_info=$(grep VmPeak /proc/$pid/status 2>/dev/null | awk '{printf "%-15s", $2/1024 " MB"}')
    if [[ -n "$mem_info" ]]; then
        printf "%-8s %-15s %-10s %-10s %-15s %-15s %-15s %-s\n" "$pid" "$user" "$cpu" "$mem" "$((rss/1024)) MB" "$((vsz/1024)) MB" "$mem_info" "$comm"
    fi
done

