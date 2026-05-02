#!/bin/bash
# Switch between tunneling chains on RF Proxy

CHAIN=$1

case $CHAIN in
  "xhttp")
    echo "Activating xhttp chain..."
    sshpass -p 'qZ4gmRizTUgQ' ssh root@89.169.4.51 "\
      systemctl stop nginx; \
      systemctl stop shadowsocks-rf-proxy; \
      cp /root/LabDoctorM/VPNDaemonRobot/vpnconfig/xray-rf-proxy-xhttp-alt.json /usr/local/etc/xray/config.json; \
      systemctl restart xray"
    ;;
    
  "ss2022")
    echo "Activating Shadowsocks-2022 chain..."
    sshpass -p 'qZ4gmRizTUgQ' ssh root@89.169.4.51 "\
      systemctl stop nginx; \
      systemctl stop xray; \
      systemctl start shadowsocks-rf-proxy"
    ;;
    
  "nginx")
    echo "Activating nginx mask chain..."
    sshpass -p 'qZ4gmRizTUgQ' ssh root@89.169.4.51 "\
      systemctl stop xray; \
      systemctl stop shadowsocks-rf-proxy; \
      cp /root/LabDoctorM/VPNDaemonRobot/vpnconfig/nginx-rf-proxy.conf /etc/nginx/nginx.conf; \
      systemctl restart nginx"
    ;;
    
  *)
    echo "Usage: $0 {xhttp|ss2022|nginx}"
    exit 1
    ;;
esac

echo "Chain $CHAIN activated"