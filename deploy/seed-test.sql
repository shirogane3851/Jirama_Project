-- Jeu de données FICTIVES pour les tests (matricules TST-xxx). Aucun secret.
BEGIN;

-- 10 employés
INSERT INTO employe (nom, prenom, matricule, telephone, email, date_embauche, solde_conge) VALUES
('Rakotoarisoa',      'Hery',      'TST-001', '0341200001', 'hery.rakotoarisoa@example.org',   '2019-03-04', 24.0),
('Randrianasolo',     'Lalao',     'TST-002', '0341200002', 'lalao.randrianasolo@example.org', '2020-08-17', 18.5),
('Rasoanaivo',        'Miora',     'TST-003', '0341200003', 'miora.rasoanaivo@example.org',    '2018-01-15', 30.0),
('Andrianarivo',      'Tsiry',     'TST-004', '0341200004', 'tsiry.andrianarivo@example.org',  '2022-05-09', 12.0),
('Rabemananjara',     'Nirina',    'TST-005', '0341200005', 'nirina.rabemananjara@example.org','2021-02-01', 22.5),
('Razafindrakoto',    'Fanja',     'TST-006', '0341200006', 'fanja.razafindrakoto@example.org','2023-09-11',  8.0),
('Ratsimbazafy',      'Toky',      'TST-007', '0341200007', 'toky.ratsimbazafy@example.org',   '2017-11-20', 27.0),
('Rajaonarison',      'Voahangy',  'TST-008', '0341200008', 'voahangy.rajaonarison@example.org','2020-01-06', 15.5),
('Randriamampionona', 'Fidy',      'TST-009', '0341200009', 'fidy.randriamampionona@example.org','2019-07-22', 19.0),
('Raveloson',         'Hanta',     'TST-010', '0341200010', 'hanta.raveloson@example.org',     '2024-03-18', 10.0)
ON CONFLICT DO NOTHING;

-- Congés (statuts : en_attente, approuve, refuse)
INSERT INTO conge (employe_id, date_debut, date_fin, motif, statut, proceed_at, proceed_by)
SELECT e.id, v.debut, v.fin, v.motif, v.statut, v.traite_le,
       CASE WHEN v.statut <> 'en_attente' THEN (SELECT id FROM compte WHERE username = 'Admin') END
FROM (VALUES
  ('TST-001', DATE '2026-11-23', DATE '2026-11-27', 'Congé annuel',           'en_attente', NULL::timestamp),
  ('TST-002', DATE '2026-11-02', DATE '2026-11-06', 'Repos',                  'approuve',   TIMESTAMP '2026-10-28 09:10'),
  ('TST-003', DATE '2026-12-21', DATE '2026-12-31', 'Fêtes de fin d''année',  'en_attente', NULL),
  ('TST-004', DATE '2026-10-12', DATE '2026-10-14', 'Affaire familiale',      'refuse',     TIMESTAMP '2026-10-08 14:30'),
  ('TST-005', DATE '2026-11-16', DATE '2026-11-18', 'Rendez-vous médical',    'approuve',   TIMESTAMP '2026-11-10 10:00'),
  ('TST-007', DATE '2026-12-01', DATE '2026-12-05', 'Voyage',                 'en_attente', NULL),
  ('TST-009', DATE '2026-09-21', DATE '2026-09-25', 'Repos',                  'approuve',   TIMESTAMP '2026-09-15 08:45')
) AS v(matricule, debut, fin, motif, statut, traite_le)
JOIN employe e ON e.matricule = v.matricule;

-- Permissions
INSERT INTO permission (employe_id, date_debut, date_fin, motif, statut, proceed_at, proceed_by)
SELECT e.id, v.debut, v.fin, v.motif, v.statut, v.traite_le,
       CASE WHEN v.statut <> 'en_attente' THEN (SELECT id FROM compte WHERE username = 'Admin') END
FROM (VALUES
  ('TST-001', DATE '2026-11-19', DATE '2026-11-19', 'Démarche administrative', 'en_attente', NULL::timestamp),
  ('TST-006', DATE '2026-11-10', DATE '2026-11-10', 'Rendez-vous',             'approuve',   TIMESTAMP '2026-11-09 16:00'),
  ('TST-008', DATE '2026-11-13', DATE '2026-11-13', 'Décès dans la famille',   'approuve',   TIMESTAMP '2026-11-12 08:30'),
  ('TST-010', DATE '2026-11-20', DATE '2026-11-20', 'Cérémonie',               'refuse',     TIMESTAMP '2026-11-12 15:20'),
  ('TST-002', DATE '2026-11-25', DATE '2026-11-26', 'Déménagement',            'en_attente', NULL)
) AS v(matricule, debut, fin, motif, statut, traite_le)
JOIN employe e ON e.matricule = v.matricule;

-- Pointages : 4 jours (9 au 12 novembre), une entrée et une sortie par employé
INSERT INTO pointage (employe_id, admin_id, type, timestamp)
SELECT e.id, a.id, t.type,
       (DATE '2026-11-09' + n) + t.heure + ((e.id * 7 + n * 3) % 20) * interval '1 minute'
FROM employe e
CROSS JOIN generate_series(0, 3) AS n
CROSS JOIN (VALUES ('entree', TIME '07:50'), ('sortie', TIME '16:30')) AS t(type, heure)
CROSS JOIN (SELECT id FROM compte WHERE username = 'Admin') AS a
WHERE e.matricule LIKE 'TST-%';

-- Avertissements (statuts : actif, leve)
INSERT INTO avertissement (pointage_id, employe_id, type, date_concernee, motif, statut, lifted_at, lifted_by, lifted_reason)
SELECT CASE WHEN v.type = 'retard'
            THEN (SELECT p.id FROM pointage p WHERE p.employe_id = e.id AND p.type = 'entree' ORDER BY p.timestamp LIMIT 1)
       END,
       e.id, v.type, v.date_concernee, v.motif, v.statut, v.leve_le,
       CASE WHEN v.statut = 'leve' THEN (SELECT id FROM compte WHERE username = 'Admin') END,
       v.raison
FROM (VALUES
  ('TST-004', 'retard',  TIMESTAMP '2026-11-10 08:45', 'Arrivée à 8h45',        'actif', NULL::timestamp,          NULL::text),
  ('TST-006', 'retard',  TIMESTAMP '2026-11-09 09:10', 'Arrivée à 9h10',        'leve',  TIMESTAMP '2026-11-11 11:00', 'Justificatif de transport fourni'),
  ('TST-009', 'absence', TIMESTAMP '2026-11-11 08:00', 'Absence non justifiée', 'actif', NULL,                       NULL),
  ('TST-010', 'retard',  TIMESTAMP '2026-11-12 08:30', 'Arrivée à 8h30',        'actif', NULL,                       NULL)
) AS v(matricule, type, date_concernee, motif, statut, leve_le, raison)
JOIN employe e ON e.matricule = v.matricule;

COMMIT;
