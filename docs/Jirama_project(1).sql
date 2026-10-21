CREATE TABLE `employe` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `matricule` varchar(15) UNIQUE NOT NULL,
  `telephone` varchar(14) UNIQUE,
  `email` varchar(100) UNIQUE,
  `date_embauche` timestamp,
  `photo_identite` varchar(255),
  `solde_conge` decimal(4,1) NOT NULL DEFAULT 0
);

CREATE TABLE `compte` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(50) UNIQUE NOT NULL,
  `employe_id` integer UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum(EMPLOYE,AGENT_POINTAGE,VALIDATEUR_CONGE,ADMIN_COMPTES) NOT NULL,
  `is_active` boolean NOT NULL DEFAULT true,
  `created_at` timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE `conge` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `employe_id` integer NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL,
  `motif` varchar(100),
  `statut` varchar(15) NOT NULL DEFAULT 'en_attente',
  `created_at` timestamp NOT NULL DEFAULT (now()),
  `proceed_at` timestamp,
  `proceed_by` integer
);

CREATE TABLE `permission` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `employe_id` integer NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL,
  `motif` varchar(100),
  `statut` varchar(15) NOT NULL DEFAULT 'en_attente',
  `created_at` timestamp NOT NULL DEFAULT (now()),
  `proceed_at` timestamp,
  `proceed_by` integer
);

CREATE TABLE `pointage` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `employe_id` integer NOT NULL,
  `admin_id` integer NOT NULL,
  `type` varchar(6) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT (now()),
  `created_at` timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE `avertissement` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `pointage_id` integer,
  `employe_id` integer NOT NULL,
  `type` varchar(20) NOT NULL,
  `date_concernee` timestamp NOT NULL,
  `motif` varchar(100),
  `statut` varchar(15) NOT NULL DEFAULT 'actif',
  `created_at` timestamp NOT NULL DEFAULT (now()),
  `lifted_at` timestamp,
  `lifted_by` integer,
  `lifted_reason` varchar(255)
);

CREATE TABLE `log` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `user_id` integer,
  `action` varchar(100) NOT NULL,
  `table_name` varchar(100),
  `record_id` integer,
  `details` varchar(500),
  `ip_address` varchar(45),
  `timestamp` timestamp NOT NULL DEFAULT (now())
);

ALTER TABLE `employe` ADD FOREIGN KEY (`id`) REFERENCES `compte` (`employe_id`);

ALTER TABLE `pointage` ADD FOREIGN KEY (`employe_id`) REFERENCES `employe` (`id`);

ALTER TABLE `pointage` ADD FOREIGN KEY (`admin_id`) REFERENCES `compte` (`id`);

ALTER TABLE `conge` ADD FOREIGN KEY (`employe_id`) REFERENCES `employe` (`id`);

ALTER TABLE `conge` ADD FOREIGN KEY (`proceed_by`) REFERENCES `compte` (`id`);

ALTER TABLE `permission` ADD FOREIGN KEY (`employe_id`) REFERENCES `employe` (`id`);

ALTER TABLE `permission` ADD FOREIGN KEY (`proceed_by`) REFERENCES `compte` (`id`);

ALTER TABLE `avertissement` ADD FOREIGN KEY (`pointage_id`) REFERENCES `pointage` (`id`);

ALTER TABLE `avertissement` ADD FOREIGN KEY (`employe_id`) REFERENCES `employe` (`id`);

ALTER TABLE `avertissement` ADD FOREIGN KEY (`lifted_by`) REFERENCES `compte` (`id`);

ALTER TABLE `log` ADD FOREIGN KEY (`user_id`) REFERENCES `compte` (`id`);
