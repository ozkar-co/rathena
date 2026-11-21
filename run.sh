#!/bin/bash
# Ir a la carpeta donde está el script
cd "$(dirname "$0")"

echo "[$(date)] --- Iniciando Fase de Limpieza de Emergencia ---"

# 1. Matar procesos huérfanos de rAthena (el -q es para que no se queje si no hay ninguno)
# El -9 garantiza que se cierren incluso si están "congelados"
killall -q -9 login-server char-server map-server 2>/dev/null

# 2. Borrar archivos de bloqueo (.pid) que impiden el arranque
rm -f .*.pid 2>/dev/null

# Pequeña pausa para que el SO libere los sockets/puertos (6900, 6121, 5121)
sleep 2

echo "[$(date)] --- Sistema Limpio. Lanzando binarios... ---"

# 3. Lanzar en orden
./login-server &
sleep 2
./char-server &
sleep 2
./map-server &

# Mantener el script vivo para que Systemd monitoree el grupo de procesos
wait
