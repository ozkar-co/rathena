-- OzRo market master projection.
-- Generated data is loaded after tools/market/build_master.py exists.
-- Canonical source remains data/market/master.jsonl + canon.yml.

CREATE TABLE IF NOT EXISTS `ozro_market_item` (
  `item_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `aegis` VARCHAR(100) NOT NULL DEFAULT '',
  `type` VARCHAR(32) NOT NULL,
  `slots` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `refineable` TINYINT(1) NOT NULL DEFAULT 0,
  `weight` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  `custom` TINYINT(1) NOT NULL DEFAULT 0,
  `price_status` ENUM('market','synthetic','manual') NOT NULL,
  `low` BIGINT UNSIGNED NOT NULL,
  `mid` BIGINT UNSIGNED NOT NULL,
  `high` BIGINT UNSIGNED NOT NULL,
  `npc_buy` BIGINT UNSIGNED NOT NULL,
  `npc_sell` BIGINT UNSIGNED NOT NULL,
  `supply_open` DOUBLE NOT NULL DEFAULT 0,
  `supply_percentile` DOUBLE NULL,
  `abundance_tier` VARCHAR(16) NOT NULL DEFAULT 'none',
  `difficulty_percentile` DOUBLE NULL,
  `difficulty_tier` VARCHAR(16) NOT NULL DEFAULT 'unknown',
  `demand_percentile` DOUBLE NULL,
  `demand_tier` VARCHAR(16) NOT NULL DEFAULT 'unknown',
  `market_pressure` DOUBLE NULL,
  `stock_hint` VARCHAR(16) NOT NULL DEFAULT 'unknown',
  `restock_weight` DOUBLE NULL,
  `market_eligible` TINYINT(1) NOT NULL DEFAULT 0,
  `npc_eligible` TINYINT(1) NOT NULL DEFAULT 1,
  `dataset_version` VARCHAR(32) NOT NULL DEFAULT 'v2',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_id`),
  KEY `idx_type_status` (`type`, `price_status`),
  KEY `idx_tiers` (`abundance_tier`, `demand_tier`),
  KEY `idx_eligible` (`market_eligible`, `npc_eligible`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ozro_market_item_tag` (
  `item_id` INT UNSIGNED NOT NULL,
  `tag` VARCHAR(48) NOT NULL,
  PRIMARY KEY (`item_id`, `tag`),
  KEY `idx_tag` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
