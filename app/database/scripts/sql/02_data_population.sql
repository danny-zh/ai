USE habitdb;

INSERT INTO `user` (username, email, password)
SELECT 'demo_user', 'demo@example.com', 'demo-password-hash-not-for-authentication'
WHERE NOT EXISTS (
    SELECT 1
    FROM `user`
    WHERE username = 'demo_user' OR email = 'demo@example.com'
);

INSERT INTO habit (name, color, description, id_user)
SELECT seed_habit.name, seed_habit.color, seed_habit.description, demo_user.id
FROM (
    SELECT 'Study' AS name, '#2563EB' AS color, 'Focused study session' AS description
    UNION ALL
    SELECT 'Read', '#7C3AED', 'Read books or articles'
    UNION ALL
    SELECT 'Workout', '#DC2626', 'Complete a physical workout'
    UNION ALL
    SELECT 'Travel', '#0891B2', 'Explore a new place'
    UNION ALL
    SELECT 'Dance', '#DB2777', 'Practice or enjoy dancing'
) AS seed_habit
JOIN `user` AS demo_user
    ON demo_user.username = 'demo_user'
WHERE NOT EXISTS (
    SELECT 1
    FROM habit AS existing_habit
    WHERE existing_habit.id_user = demo_user.id
      AND existing_habit.name = seed_habit.name
);

INSERT INTO habit_log (id_habit, id_user, habit_duration, log_date)
WITH RECURSIVE august_dates AS (
    SELECT DATE('2026-08-01') AS log_date
    UNION ALL
    SELECT log_date + INTERVAL 1 DAY
    FROM august_dates
    WHERE log_date < '2026-08-31'
)
SELECT
    habit.id,
    habit.id_user,
    30 + (CRC32(CONCAT(habit.name, august_dates.log_date, 'duration')) % 7) * 15,
    august_dates.log_date
FROM habit
JOIN `user` AS demo_user
    ON demo_user.id = habit.id_user
CROSS JOIN august_dates
WHERE demo_user.username = 'demo_user'
  AND habit.name IN ('Study', 'Read', 'Workout', 'Travel', 'Dance')
  AND CRC32(CONCAT(habit.name, august_dates.log_date, 'completion')) % 100 < 55
ON DUPLICATE KEY UPDATE
    id_user = VALUES(id_user),
    habit_duration = VALUES(habit_duration);