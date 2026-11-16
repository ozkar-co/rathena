#!/usr/bin/env python3
"""Generate the Garrett NPC script from the precomputed mission table.

The output is written as Latin-1 because rAthena scripts on this server use that
encoding. Run this after regenerating garrett-missions.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT.parent / "ozro-site" / "assets" / "items" / "garrett-missions.json"
OUTPUT = ROOT / "npc" / "custom" / "ozro" / "trasher.txt"


def csv(values) -> str:
    return ", ".join(str(value) for value in values)


def main() -> None:
    data = json.loads(TABLE.read_text(encoding="utf-8"))

    offers = {"abundant": [], "common": [], "uncommon": [], "rare": []}
    for row in data["dailyOffers"]:
        offers[row["tier"]].append(row)

    missions = {"common": [], "uncommon": [], "rare": []}
    for row in data["missions"]:
        missions[row["tier"]].append(row)

    replacements = {}
    for tier in offers:
        replacements[f"@{tier.upper()}_IDS@"] = csv(row["id"] for row in offers[tier])
        replacements[f"@{tier.upper()}_PRICES@"] = csv(
            row["unitPrice"] for row in offers[tier]
        )
    for tier in missions:
        replacements[f"@M{tier.upper()}_IDS@"] = csv(row["id"] for row in missions[tier])
        replacements[f"@M{tier.upper()}_QTY@"] = csv(
            row["quantity"] for row in missions[tier]
        )
        replacements[f"@M{tier.upper()}_PAY@"] = csv(
            row["payout"] for row in missions[tier]
        )

    script = TEMPLATE
    for key, value in replacements.items():
        script = script.replace(key, value)

    OUTPUT.write_text(script, encoding="latin-1")
    print(f"wrote {OUTPUT} ({len(script)} bytes, Latin-1)")


TEMPLATE = r'''//===== OzRo Script ==========================================
//= Garrett el Recolector
//===== Description: =========================================
//= Compra chatarra por cuenta. Cinco ofertas diarias con cap de
//= 500.000 zeny y una misión diaria de 6 horas.
//= Los datos se precalculan en:
//= ozro-site/assets/items/garrett-missions.json
//= Las variables viejas TRSH_* quedan como historial y no se usan.
//============================================================

geffen,143,70,3	script	Garrett	1_M_SIGN1,{

	.@today = gettime(DT_YYYYMMDD);
	callsub L_ResetDay, .@today;

	if (#GARRETT_MISSION_ACTIVE == 1) {
		callsub L_MissionStatus, .@today;
		if (#GARRETT_MISSION_ACTIVE == 1) close;
	}

	mes .npc_name$;
	if (OZRO_KARMA < 0) {
		mes "Tú otra vez...";
		mes "No me gusta tu aura, pero el negocio es el negocio.";
	} else if (OZRO_KARMA > 0) {
		mes "Ah, " + strcharinfo(0) + ". Me alegra verte.";
		mes "Tienes buen ojo para lo que vale la pena, eso se nota.";
	} else {
		mes "Bienvenido, forastero.";
		mes "Dicen que la basura de un hombre es el tesoro de otro.";
	}
	mes "Hoy tengo cinco cosas en el ojo.";
	mes "Presupuesto de compras: " + (.daily_cap - #GARRETT_SPENT) + " zeny.";
	next;

	switch (select("Ver ofertas del día:Misión:Sobre tu negocio:Marcharme")) {
	case 1:
		callsub L_Offers;
		break;
	case 2:
		callsub L_MissionMenu, .@today;
		break;
	case 3:
		mes .npc_name$;
		mes "Llevo " + #GARRETT_TOTAL_SPENT + " zeny invertidos en chatarra de aventureros.";
		mes "Contigo he cerrado " + #GARRETT_TRADES + " tratos. Cada uno cuenta.";
		mes "Misiones completadas: " + #GARRETT_MISSIONS_DONE + ".";
		break;
	case 4:
		mes .npc_name$;
		mes "Buen viaje. La basura de hoy puede ser la riqueza de mañana.";
		break;
	}
	close;

L_Offers:
	if (#GARRETT_SPENT >= .daily_cap) {
		mes .npc_name$;
		mes "Amigo, ya no me queda una moneda en la bolsa hoy.";
		mes "Vuelve mañana. Siempre hay basura nueva que vale la pena.";
		next;
		return;
	}

	mes .npc_name$;
	mes "Hoy compro:";
	mes "1) " + getitemname(#GARRETT_OFFER0) + " - " + #GARRETT_PRICE0 + " zeny c/u";
	mes "2) " + getitemname(#GARRETT_OFFER1) + " - " + #GARRETT_PRICE1 + " zeny c/u";
	mes "3) " + getitemname(#GARRETT_OFFER2) + " - " + #GARRETT_PRICE2 + " zeny c/u";
	mes "4) " + getitemname(#GARRETT_OFFER3) + " - " + #GARRETT_PRICE3 + " zeny c/u";
	mes "5) " + getitemname(#GARRETT_OFFER4) + " - " + #GARRETT_PRICE4 + " zeny c/u";
	mes "Presupuesto restante: " + (.daily_cap - #GARRETT_SPENT) + " zeny.";
	next;

	.@sel = select("Oferta 1:Oferta 2:Oferta 3:Oferta 4:Oferta 5:Volver") - 1;
	if (.@sel == 5) return;
	if (.@sel == 0) {
		.@item = #GARRETT_OFFER0;
		.@price = #GARRETT_PRICE0;
	} else if (.@sel == 1) {
		.@item = #GARRETT_OFFER1;
		.@price = #GARRETT_PRICE1;
	} else if (.@sel == 2) {
		.@item = #GARRETT_OFFER2;
		.@price = #GARRETT_PRICE2;
	} else if (.@sel == 3) {
		.@item = #GARRETT_OFFER3;
		.@price = #GARRETT_PRICE3;
	} else {
		.@item = #GARRETT_OFFER4;
		.@price = #GARRETT_PRICE4;
	}

	if (.@item == 0 || .@price <= 0) {
		mes .npc_name$;
		mes "Esa oferta ya no está disponible.";
		next;
		return;
	}

	mes .npc_name$;
	mes "¿Cuántos " + getitemname(.@item) + " me vendes?";
	mes "Tienes " + countitem(.@item) + " en el inventario.";
	next;

	input .@amount;
	if (.@amount <= 0) {
		mes .npc_name$;
		mes "Vamos, hablemos en serio.";
		next;
		return;
	}
	if (countitem(.@item) < .@amount) {
		mes .npc_name$;
		mes "No tienes tantos. Solo llevas " + countitem(.@item) + ".";
		next;
		return;
	}

	.@remaining = .daily_cap - #GARRETT_SPENT;
	.@max = .@remaining / .@price;
	if (.@max <= 0) {
		mes .npc_name$;
		mes "Con lo que me queda hoy no puedo comprar ni uno.";
		next;
		return;
	}
	if (.@amount > .@max) {
		mes .npc_name$;
		mes "Solo puedo comprar " + .@max + " con lo que me queda hoy.";
		next;
		.@amount = .@max;
	}

	.@total = .@price * .@amount;
	mes .npc_name$;
	mes .@amount + " x " + getitemname(.@item) + " = " + .@total + " zeny. ¿Trato?";
	next;
	if (select("Trato hecho", "Paso") == 2) {
		mes .npc_name$;
		mes "La puerta sigue abierta.";
		next;
		return;
	}

	delitem .@item, .@amount;
	Zeny += .@total;
	#GARRETT_SPENT += .@total;
	#GARRETT_TOTAL_SPENT += .@total;
	#GARRETT_TRADES++;

	if (.@sel == 0 && #GARRETT_SOLD0 == 0) {
		#GARRETT_SOLD0 = 1;
		callsub L_UniqueTrade;
	} else if (.@sel == 1 && #GARRETT_SOLD1 == 0) {
		#GARRETT_SOLD1 = 1;
		callsub L_UniqueTrade;
	} else if (.@sel == 2 && #GARRETT_SOLD2 == 0) {
		#GARRETT_SOLD2 = 1;
		callsub L_UniqueTrade;
	} else if (.@sel == 3 && #GARRETT_SOLD3 == 0) {
		#GARRETT_SOLD3 = 1;
		callsub L_UniqueTrade;
	} else if (.@sel == 4 && #GARRETT_SOLD4 == 0) {
		#GARRETT_SOLD4 = 1;
		callsub L_UniqueTrade;
	}

	mes .npc_name$;
	mes "Un placer hacer negocios.";
	if (#GARRETT_SPENT >= .daily_cap) {
		mes "Con eso agoto el presupuesto de hoy.";
		mes "Mañana habrá más oportunidades.";
	}
	next;
	return;

L_UniqueTrade:
	#GARRETT_UNIQUE_TRADES++;
	OZRO_KARMA += 1;
	if (#GARRETT_UNIQUE_TRADES % .trades_for_coin == 0) {
		getitem "Ozro_Bronze_Coin", 1;
		mes "Por cierto... eres un sujeto agradable.";
		mes "Creo que esto te sirve más a ti que a mi.";
	}
	return;

L_MissionStatus:
	.@today = getarg(0);
	.@left = #GARRETT_MISSION_END - gettimetick(2);
	if (.@left <= 0) {
		#GARRETT_MISSION_ACTIVE = 0;
		#GARRETT_MISSION_DAY = .@today;
		mes .npc_name$;
		mes "Llegaste tarde.";
		mes "La basura ya no me interesa. Pero las compras del día siguen abiertas.";
		next;
		return;
	}

	.@have = countitem(#GARRETT_MISSION_ITEM);
	if (.@have >= #GARRETT_MISSION_QTY) {
		mes .npc_name$;
		mes "Veo que ya tienes " + #GARRETT_MISSION_QTY + " x " + getitemname(#GARRETT_MISSION_ITEM) + ".";
		mes "¿Cerramos el contrato?";
		next;
		if (select("Cerrar el contrato", "Todavía no") == 1) {
			delitem #GARRETT_MISSION_ITEM, #GARRETT_MISSION_QTY;
			Zeny += #GARRETT_MISSION_PAY;
			#GARRETT_MISSION_ACTIVE = 0;
			#GARRETT_MISSION_DAY = .@today;
			#GARRETT_MISSIONS_DONE++;
			#GARRETT_MISSION_EARNED += #GARRETT_MISSION_PAY;
			mes .npc_name$;
			mes "Trato hecho. Aquí tienes " + #GARRETT_MISSION_PAY + " zeny.";
			mes "No tendré otra misión para ti hasta mañana.";
			next;
			return;
		}
	}

	.@hours = .@left / 3600;
	.@mins = (.@left % 3600) / 60;
	mes .npc_name$;
	mes "Todavía estás trabajando para mí.";
	mes "Te quedan " + .@hours + "h " + .@mins + "m.";
	mes "Trae " + #GARRETT_MISSION_QTY + " x " + getitemname(#GARRETT_MISSION_ITEM) + ".";
	mes "Llevas " + .@have + ".";
	next;
	if (select("Cancelar la misión", "Seguir buscando") == 1) {
		mes .npc_name$;
		mes "Si cancelas, no tendré otra misión para ti hasta mañana.";
		mes "Las compras del día quedarán abiertas.";
		next;
		if (select("Sí, cancelar", "No, continuar") == 1) {
			#GARRETT_MISSION_ACTIVE = 0;
			#GARRETT_MISSION_DAY = .@today;
			mes .npc_name$;
			mes "Está bien. La basura puede esperar.";
			next;
			return;
		}
	}
	close;

L_MissionMenu:
	.@today = getarg(0);
	if (#GARRETT_MISSION_DAY == .@today) {
		mes .npc_name$;
		mes "Hoy ya no tengo misiones para ti. Vuelve mañana.";
		next;
		return;
	}
	if (#GARRETT_CONTRACT_ITEM0 == 0 || #GARRETT_CONTRACT_ITEM1 == 0 || #GARRETT_CONTRACT_ITEM2 == 0) {
		mes .npc_name$;
		mes "Hoy no tengo contratos disponibles.";
		next;
		return;
	}

	mes .npc_name$;
	mes "Tengo tres contratos. Elige uno:";
	mes "1) Común: " + getitemname(#GARRETT_CONTRACT_ITEM0) + " x" + #GARRETT_CONTRACT_QTY0 + " - " + #GARRETT_CONTRACT_PAY0 + " zeny";
	mes "2) Poco común: " + getitemname(#GARRETT_CONTRACT_ITEM1) + " x" + #GARRETT_CONTRACT_QTY1 + " - " + #GARRETT_CONTRACT_PAY1 + " zeny";
	mes "3) Raro: " + getitemname(#GARRETT_CONTRACT_ITEM2) + " x" + #GARRETT_CONTRACT_QTY2 + " - " + #GARRETT_CONTRACT_PAY2 + " zeny";
	mes "Tienes 6 horas para conseguirlos. Si fallas o cancelas, no habrá otra misión hasta mañana.";
	next;

	.@sel = select("Contrato 1:Contrato 2:Contrato 3:Volver") - 1;
	if (.@sel == 3) return;
	if (.@sel == 0) {
		.@item = #GARRETT_CONTRACT_ITEM0;
		.@qty = #GARRETT_CONTRACT_QTY0;
		.@pay = #GARRETT_CONTRACT_PAY0;
		.@tier$ = "Común";
	} else if (.@sel == 1) {
		.@item = #GARRETT_CONTRACT_ITEM1;
		.@qty = #GARRETT_CONTRACT_QTY1;
		.@pay = #GARRETT_CONTRACT_PAY1;
		.@tier$ = "Poco común";
	} else {
		.@item = #GARRETT_CONTRACT_ITEM2;
		.@qty = #GARRETT_CONTRACT_QTY2;
		.@pay = #GARRETT_CONTRACT_PAY2;
		.@tier$ = "Raro";
	}

	mes .npc_name$;
	mes "Contrato " + .@tier$ + ":";
	mes "- " + getitemname(.@item) + " x" + .@qty;
	mes "- Pago: " + .@pay + " zeny";
	mes "- Tiempo: 6 horas";
	mes "¿Aceptas?";
	next;
	if (select("Aceptar", "Rechazar") == 2) {
		mes .npc_name$;
		mes "Sin prisa. Los buenos tratos requieren calma.";
		next;
		return;
	}

	#GARRETT_MISSION_ITEM = .@item;
	#GARRETT_MISSION_QTY = .@qty;
	#GARRETT_MISSION_PAY = .@pay;
	#GARRETT_MISSION_ACTIVE = 1;
	#GARRETT_MISSION_DAY = .@today;
	#GARRETT_MISSION_END = gettimetick(2) + .mission_seconds;
	mes .npc_name$;
	mes "Aceptado. Tienes 6 horas.";
	mes "Si ya tienes los items, habla conmigo y cerramos el trato.";
	next;
	return;

L_ResetDay:
	.@today = getarg(0);
	if (#GARRETT_DAY == .@today && #GARRETT_OFFER0 != 0) return;

	#GARRETT_DAY = .@today;
	#GARRETT_SPENT = 0;
	#GARRETT_SOLD0 = 0;
	#GARRETT_SOLD1 = 0;
	#GARRETT_SOLD2 = 0;
	#GARRETT_SOLD3 = 0;
	#GARRETT_SOLD4 = 0;

	.@idx = rand(.abundant_count);
	#GARRETT_OFFER0 = .abundant_id[.@idx];
	#GARRETT_PRICE0 = .abundant_price[.@idx];
	do {
		.@idx = rand(.abundant_count);
	} while (.abundant_id[.@idx] == #GARRETT_OFFER0);
	#GARRETT_OFFER1 = .abundant_id[.@idx];
	#GARRETT_PRICE1 = .abundant_price[.@idx];

	.@idx = rand(.common_count);
	#GARRETT_OFFER2 = .common_id[.@idx];
	#GARRETT_PRICE2 = .common_price[.@idx];

	.@idx = rand(.uncommon_count);
	#GARRETT_OFFER3 = .uncommon_id[.@idx];
	#GARRETT_PRICE3 = .uncommon_price[.@idx];

	.@idx = rand(.rare_count);
	#GARRETT_OFFER4 = .rare_id[.@idx];
	#GARRETT_PRICE4 = .rare_price[.@idx];

	.@idx = rand(.mcommon_count);
	#GARRETT_CONTRACT_ITEM0 = .mcommon_id[.@idx];
	#GARRETT_CONTRACT_QTY0 = .mcommon_qty[.@idx];
	#GARRETT_CONTRACT_PAY0 = .mcommon_pay[.@idx];

	.@idx = rand(.muncommon_count);
	#GARRETT_CONTRACT_ITEM1 = .muncommon_id[.@idx];
	#GARRETT_CONTRACT_QTY1 = .muncommon_qty[.@idx];
	#GARRETT_CONTRACT_PAY1 = .muncommon_pay[.@idx];

	.@idx = rand(.mrare_count);
	#GARRETT_CONTRACT_ITEM2 = .mrare_id[.@idx];
	#GARRETT_CONTRACT_QTY2 = .mrare_qty[.@idx];
	#GARRETT_CONTRACT_PAY2 = .mrare_pay[.@idx];

	return;

OnInit:
	.npc_name$ = "[ ^0000FFGarrett el Recolector^000000 ]";
	.daily_cap = 500000;
	.mission_seconds = 21600;
	.trades_for_coin = 10;

	setarray .abundant_id[0], @ABUNDANT_IDS@;
	setarray .abundant_price[0], @ABUNDANT_PRICES@;
	setarray .common_id[0], @COMMON_IDS@;
	setarray .common_price[0], @COMMON_PRICES@;
	setarray .uncommon_id[0], @UNCOMMON_IDS@;
	setarray .uncommon_price[0], @UNCOMMON_PRICES@;
	setarray .rare_id[0], @RARE_IDS@;
	setarray .rare_price[0], @RARE_PRICES@;

	setarray .mcommon_id[0], @MCOMMON_IDS@;
	setarray .mcommon_qty[0], @MCOMMON_QTY@;
	setarray .mcommon_pay[0], @MCOMMON_PAY@;
	setarray .muncommon_id[0], @MUNCOMMON_IDS@;
	setarray .muncommon_qty[0], @MUNCOMMON_QTY@;
	setarray .muncommon_pay[0], @MUNCOMMON_PAY@;
	setarray .mrare_id[0], @MRARE_IDS@;
	setarray .mrare_qty[0], @MRARE_QTY@;
	setarray .mrare_pay[0], @MRARE_PAY@;

	.abundant_count = getarraysize(.abundant_id);
	.common_count = getarraysize(.common_id);
	.uncommon_count = getarraysize(.uncommon_id);
	.rare_count = getarraysize(.rare_id);
	.mcommon_count = getarraysize(.mcommon_id);
	.muncommon_count = getarraysize(.muncommon_id);
	.mrare_count = getarraysize(.mrare_id);
	return;
}
'''


if __name__ == "__main__":
    main()
