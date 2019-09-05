# querys
QUERY_GPU = "nvidia-smi \
    --query-gpu=timestamp,gpu_uuid,count,name,pstate,temperature.gpu,utilization.gpu,memory.used,memory.total \
    --format=csv,noheader,nounits"
QUERY_APP = "nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader"
QUERY_APP_PROCESS = """
        a=($(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | awk '{print $1,$2,$3}' FS=', ' OFS=','))
        for item in $a
        do
            ps=$(ps --noheader -o "pid,user,%cpu,%mem,etime,command" -p $(echo $item | awk '{print $2}' FS=',') )
            echo $item | awk '{printf "%s, %s, ", $1, $3}' FS="," RS="\n" 
            echo $ps | awk 'BEGIN {OFS=", "} {$1=$1; print}' RS="\n"
        done;
        """