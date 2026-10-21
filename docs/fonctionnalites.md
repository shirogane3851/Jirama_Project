### En tant qu’employé

1. Je peux envoyer des demandes de congés et de permissions.
2. Je peux demander des codes afin de valider mon heure d’entrée et de sortie.
3. Je dispose d’une interface permettant de consulter mes soldes de congés.

### En tant qu’admin_pointage

1. Je peux vérifier les informations des employés et valider leurs heures d’entrée et de sortie à l’aide de leur code à 6 chiffres.
2. Je peux accéder à un tableau de bord permettant de consulter les statistiques.

### En tant qu’admin_congés

1. Je peux autoriser ou refuser les demandes de congés et de permissions des employés via une interface.
2. Je ne peux pas autoriser ma propre demande.

### En tant qu’admin_recrutement

1. Je peux créer des comptes utilisateurs avec un mot de passe temporaire.

### Règles du pointage

**R1.** L’heure enregistrée est celle du serveur au moment de la validation. Elle ne dépend jamais de l’heure fournie par le téléphone.

**R2.** Un code comporte 6 chiffres, est valable pendant 60 secondes et ne peut être utilisé qu’une seule fois. Un employé ne peut avoir qu’un seul code actif. Le code est stocké sous forme hachée.

**R3.** Une saisie erronée, un code expiré ou un code déjà utilisé invalide le code actif. Le même message est affiché dans les trois cas. L’employé doit alors demander un nouveau code. Chaque tentative invalide est journalisée.

**R4.** L’entrée et la sortie alternent automatiquement. Le jour est déterminé selon l’heure locale du fuseau horaire `Indian/Antananarivo`.

**R5.** Si le dernier pointage correspond à une entrée d’un jour précédent, le serveur crée un avertissement « sortie oubliée » pour ce jour, puis enregistre le nouveau pointage comme une entrée.

**R6.** Les avertissements sont visibles par l’employé et par l’admin_pointage.

**R7.** Les admin_pointage ne pointent pas. Ils ne peuvent donc pas demander de code et sont exclus du tableau de bord des horaires.

**R8.** Chaque pointage enregistre l’admin_pointage qui l’a validé.

**R9.** Les comptes administrateurs sont créés uniquement à l’aide du script en ligne de commande. L’admin_recrutement ne peut créer que des comptes employés.

**R10.** Les avertissements sont comptabilisés par mois civil local, selon le jour concerné, c’est-à-dire le jour de la sortie oubliée.

**R11.** Un avertissement peut être levé par un admin_pointage, avec un motif obligatoire qui est journalisé.

**R12.** Au troisième avertissement actif au cours d’un mois, les avertissements de ce mois deviennent définitifs et ne peuvent plus être levés. L’employé est alors directement marqué dans le tableau de bord. Aucune sanction n’est appliquée automatiquement.

**R13.** L’admin_pointage identifie l’employé à l’aide d’une recherche limitée au nom ou au matricule, puis saisit le code. Le code est vérifié uniquement pour l’employé sélectionné.
