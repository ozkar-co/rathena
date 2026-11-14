// Copyright (c) rAthena Dev Teams - Licensed under GNU GPL
// For more information, see LICENCE in the main folder

#ifndef CONFIG_CUSTOM_DEFINES_PRE_HPP
#define CONFIG_CUSTOM_DEFINES_PRE_HPP

/**
 * rAthena configuration file (http://rathena.org)
 * For detailed guidance on these check http://rathena.org/wiki/SRC/config/
 **/

// OzRagnarok: PACKETVER oficial. El cliente desplegado es Ragexe 2019-06-05.
// Si se pasa --enable-packetver al configure, esa definicion tiene prioridad.
#ifndef PACKETVER
	#define PACKETVER 20190605
#endif

// OzRagnarok: bloquea los 4th jobs. No son soportados por el cliente 2019
// y en esta version de rAthena estan bugueados. Se bloquea en pc_jobchange,
// asi que cubre @jobchange, scripts y cualquier job master futuro.
#define DISABLE_4TH_JOBS

// OzRagnarok: desactiva los iconos de questinfo (0x446) sobre los NPCs.
// Comentar esta linea para volver a mostrarlos.
#define DISABLE_QUESTINFO_MARKERS

#endif /* CONFIG_CUSTOM_DEFINES_PRE_HPP */
