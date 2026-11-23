# TCP throughput forwarding
ssh -i ~/.ssh/vpn_research_key \
    -N -L 5202:127.0.0.1:5201 \
    USER@KALI_IP

# TCP latency forwarding
ssh -i ~/.ssh/vpn_research_key \
    -N -L 5002:127.0.0.1:5001 \
    USER@KALI_IP

# HTTP packet visibility forwarding
ssh -i ~/.ssh/vpn_research_key \
    -N -L 8001:127.0.0.1:8000 \
    USER@KALI_IP
