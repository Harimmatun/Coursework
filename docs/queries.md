# Документація складних SQL-запитів

У цьому розділі наведено опис ключових аналітичних запитів, що використовуються в системі для генерації звітів. Кожен запит супроводжується бізнес-обґрунтуванням, детальним поясненням синтаксису та прикладом результату.

---

### Запит 1: Аналіз успішності студентів (Student Performance Report)

**Бізнес-питання:**
Яка середня успішність кожного студента в системі та наскільки вони активні (кількість зданих робіт)? Це дозволяє виявити студентів, яким потрібна допомога, або навпаки — претендентів на відмінність.

**SQL-запит:**
```sql
SELECT 
    u.full_name AS student_name,
    u.email,
    COUNT(s.id) AS submitted_works_count,
    ROUND(AVG(s.score), 2) AS average_score,
    MAX(s.score) AS best_score
FROM users u
JOIN submissions s ON u.id = s.student_id
WHERE u.role = 'STUDENT'
GROUP BY u.id, u.full_name, u.email
HAVING COUNT(s.id) > 0
ORDER BY average_score DESC;
```

**Детальне пояснення:**
1.  **`JOIN submissions s ON u.id = s.student_id`**: Ми об'єднуємо таблицю користувачів (`users`) з таблицею зданих робіт (`submissions`). Використовується `INNER JOIN` (за замовчуванням), тому студенти без жодної зданої роботи не потраплять у звіт.
2.  **`WHERE u.role = 'STUDENT'`**: Додатковий фільтр для гарантії, що ми аналізуємо саме студентів.
3.  **Агрегатні функції:**
    * `COUNT(s.id)`: Рахує загальну кількість зданих домашніх завдань.
    * `AVG(s.score)`: Обчислює середнє арифметичне всіх оцінок.
    * `ROUND(..., 2)`: Округлює середній бал до 2 знаків після коми для зручності читання.
    * `MAX(s.score)`: Знаходить найкращу оцінку студента.
4.  **`GROUP BY`**: Групування відбувається за унікальним ID студента (та його іменем/поштою), щоб агрегатні функції рахувались окремо для кожної людини.
5.  **`ORDER BY average_score DESC`**: Сортування від "відмінників" до студентів з найнижчим балом.

**Приклад виводу:**
| student_name | email | submitted_works_count | average_score | best_score |
|---|---|---|---|---|
| Олександр Коваленко | alex.kov@test.com | 5 | 98.50 | 100 |
| Марія Петренко | maria.p@test.com | 3 | 85.33 | 90 |
| Іван Сидоренко | ivan.s@test.com | 4 | 72.00 | 80 |

---

### Запит 2: Фінансовий звіт по інструкторах (Instructor Revenue)

**Бізнес-питання:**
Який загальний дохід згенерував кожен викладач через свої курси? (Припускається, що дохід = ціна курсу * кількість записаних студентів).

**SQL-запит:**
```sql
SELECT 
    u.full_name AS instructor_name,
    COUNT(DISTINCT c.id) AS courses_created,
    COUNT(e.id) AS total_enrollments,
    SUM(c.price) AS total_revenue
FROM users u
JOIN courses c ON u.id = c.instructor_id
JOIN enrollments e ON c.id = e.course_id
WHERE u.role = 'INSTRUCTOR'
GROUP BY u.id, u.full_name
ORDER BY total_revenue DESC;
```

**Детальне пояснення:**
1.  **Багаторівневий JOIN:**
    * `users` -> `courses`: Знаходимо всі курси, створені викладачем.
    * `courses` -> `enrollments`: Знаходимо всіх студентів, записаних на ці курси.
2.  **`SUM(c.price)`**: Це ключовий момент. Оскільки ми приєднали таблицю `enrollments`, рядок з курсом дублюється для кожного студента. Сумуючи `price` для кожного рядка `enrollment`, ми отримуємо реальний валовий дохід.
3.  **`COUNT(DISTINCT c.id)`**: Рахує, скільки унікальних курсів веде викладач (щоб не рахувати той самий курс багато разів через велику кількість студентів).
4.  **Логіка бізнесу:** Цей запит показує не просто "хто створив більше курсів", а "чиї курси краще продаються".

**Приклад виводу:**
| instructor_name | courses_created | total_enrollments | total_revenue |
|---|---|---|---|
| Проф. Дамблдор | 2 | 150 | 75000 |
| Северус Снейп | 1 | 45 | 15500 |
| Мінерва Макґонеґел | 3 | 10 | 5000 |

---

### Запит 3: Популярність курсів та наповненість (Course Analytics)

**Бізнес-питання:**
Які курси є найбільш популярними (мають найбільше активних студентів) і яка середня вартість залучення студента?

**SQL-запит:**
```sql
SELECT 
    c.title AS course_title,
    c.price,
    COUNT(e.id) AS active_students,
    (c.price * COUNT(e.id)) AS potential_revenue
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'ACTIVE'
GROUP BY c.id, c.title, c.price
ORDER BY active_students DESC, c.price DESC;
```

**Детальне пояснення:**
1.  **`LEFT JOIN`**: Використано замість `INNER JOIN`. Це критично важливо, щоб у звіті з'явилися навіть нові курси, на які ще ніхто не записався (у них буде 0 студентів). `INNER JOIN` просто приховав би їх.
2.  **`AND e.status = 'ACTIVE'`**: Фільтрація відбувається прямо в умові приєднання (JOIN condition). Ми рахуємо лише тих, хто навчається зараз, ігноруючи відрахованих (`DROPPED`).
3.  **Обчислюване поле:** `(c.price * COUNT(e.id))` — обчислення потенційного прибутку прямо в запиті без використання `SUM` (альтернативний підхід до Запиту 2, але в розрізі курсів).
4.  **Стратегія індексування:** Для прискорення цього запиту в базі даних створено індекси на полях `courses.id`, `enrollments.course_id` та `enrollments.status`.

**Приклад виводу:**
| course_title | price | active_students | potential_revenue |
|---|---|---|---|
| Python Basics | 500 | 120 | 60000 |
| Advanced SQL | 1200 | 45 | 54000 |
| Machine Learning | 2000 | 15 | 30000 |
| History of Art | 300 | 0 | 0 |