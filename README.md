# Grand Line Adventurers' Guild — One Piece

A web application for managing a fantasy adventure guild, themed as **One Piece**.

The app is dedicated to a single **fictional week** of activity from Monday to  Sunday. The days are
not tied to real calendar dates; the app uses a **simulated current day and time** that is set
in the code (like its not a live clock)

Adventurers explore the weekly quest program and join quest sessions. The **Guild Master**
creates quests and schedules their sessions. A **Guild Council** administrator can view  things about the platform mainly for checking like the guild's registered adventurers and  its full program and some platform statistics.


## 1. Technology used for the app

- **Backend:** Python + Flask + sqlite3 
- **Frontend:** HTML , CSS , JavaScript (Jinja2 templates , Bootstrap 5.3.8 and Bootstrap Icons , Google Fonts )
- **Database:** `fantasy.db` created and seeded from the app DB Browser .

## 2. Deployed URL in pythonanywhere

> **https://glorianbici1234.pythonanywhere.com/**  


## 3. Guide on how to run it locally 

Open the project folder in a IDE and run the following command below in the terminal of app.py file

```bash
pip install -r requirements.txt
flask run --debug --port 5055
```
Then open **http://127.0.0.1:5000**.

## 4. Simulated current day and time

It is set  at the top of `app.py`:

**Simulated now = Wednesday, 17:30.**
s

The only   thing the simulated clock is used for is that an adventurer can **modify or cancel** a
participation **only if its session starts more than 8 hours after** the simulated now. 


## 5. Sample accounts provided (credentials)

| Role          | Name              | Email                | Password       |
|---------------|-------------------|----------------------|----------------|
| Guild Master  | Red-Haired Shanks | `shanks@guild.com`   | `redhair123`   |
| Guild Council | The Five Elders   | `council@guild.com`  | `council123`   |
| Adventurer    | Monkey D. Luffy   | `luffy@strawhat.com` | `gomugomu123`  |
| Adventurer    | Roronoa Zoro      | `zoro@strawhat.com`  | `santoryu123`  |
| Adventurer    | Nami              | `nami@strawhat.com`  | `mikan123`     |
| Adventurer    | Nico Robin        | `robin@strawhat.com` | `poneglyph123` |

> On the **login page**, first choose the **Profile** (Adventurer / Guild Master / Guild Council),
> then enter the email + password as provided here .

Registration on the site only ever creates **adventurers** 


## 6. The fixed  options provided for  quest creation and their sessions 

- **Locations (3):** Elbaf , Wano Country , Egghead Island
- **Party roles & capacity per session:** Warrior 4 , Mage 3 , Healer 2
- **Quest types:** combat, exploration, puzzle, stealth, magic, survival
- **Difficulty levels:** easy, medium, hard, legendary
- Each adventurer may reserve **1 or 2 places** (2 = bring a companion, same role), join **at most 3
  sessions** in the week, and cannot join two sessions that overlap in time.

---

## 7. Quest and sessions already inserted in the  database of the app

### Quests (6)

| Quest                        | Type        | Difficulty | Duration |
|------------------------------|-------------|------------|----------|
| Onigashima Raid              | combat      | hard       | 120 min  |
| Escape Egghead               | survival    | legendary  | 150 min  |
| Shadows of the Fire Festival | stealth     | medium     | 90 min   |
| Punk Records Cipher          | puzzle      | easy       | 60 min   |
| Rite of the Warrior Giants   | magic       | hard       | 120 min  |
| Voyage to Elbaf              | exploration | medium     | 90 min   |

### Quest sessions (17 , with condition of at least 2 per day, quests have multiple locations)

| Day | Time  | Quest                        | Location       |
|-----|-------|------------------------------|----------------|
| Mon | 10:00 | Punk Records Cipher          | Egghead Island |
| Mon | 18:00 | Onigashima Raid              | Wano Country   |
| Tue | 09:00 | Voyage to Elbaf              | Elbaf          |
| Tue | 20:00 | Shadows of the Fire Festival | Wano Country   |
| Wed | 09:00 | Punk Records Cipher          | Elbaf          |
| Wed | 20:00 | Escape Egghead               | Egghead Island |
| Thu | 10:00 | Onigashima Raid              | Egghead Island |
| Thu | 10:00 | Onigashima Raid              | Elbaf          |
| Thu | 14:00 | Onigashima Raid              | Egghead Island |
| Thu | 16:00 | Rite of the Warrior Giants   | Elbaf          |
| Fri | 10:00 | Punk Records Cipher          | Wano Country   |
| Fri | 18:00 | Shadows of the Fire Festival | Elbaf          |
| Sat | 10:00 | Voyage to Elbaf              | Wano Country   |
| Sat | 15:00 | Escape Egghead               | Wano Country   |
| Sat | 21:00 | Onigashima Raid              | Elbaf          |
| Sun | 10:00 | Rite of the Warrior Giants   | Egghead Island |
| Sun | 17:00 | Voyage to Elbaf              | Egghead Island |

### Existing participations (bookings)

| Adventurer      | Session (day / time / location) | Quest                        | Role    | Places | Status    |
|-----------------|----------------------------------|------------------------------|---------|--------|-----------|
| Monkey D. Luffy | Mon 18:00 · Wano Country         | Onigashima Raid              | Warrior | 1      | active    |
| Monkey D. Luffy | Thu 10:00 · Egghead Island       | Onigashima Raid              | Healer  | 2      | active    |
| Monkey D. Luffy | Sat 15:00 · Wano Country         | Escape Egghead               | Mage    | 1      | active    |
| Roronoa Zoro    | Tue 20:00 · Wano Country         | Shadows of the Fire Festival | Warrior | 1      | active    |
| Roronoa Zoro    | Thu 16:00 · Elbaf                | Rite of the Warrior Giants   | Mage    | 2      | active    |
| Nami            | Mon 10:00 · Egghead Island       | Punk Records Cipher          | Healer  | 1      | active    |
| Nami            | Wed 20:00 · Egghead Island       | Escape Egghead               | Warrior | 1      | active    |
| Nami            | Thu 10:00 · Egghead Island       | Onigashima Raid              | Warrior | 1      | active    |
| Nico Robin      | Fri 18:00 · Elbaf               | Shadows of the Fire Festival | Healer  | 1      | cancelled |
| Nico Robin      | Sun 10:00 · Egghead Island       | Rite of the Warrior Giants   | Warrior | 1      | active    |

Resulting per-adventurer state:
- **Luffy** and **Nami** each have **3 active** sessions → cannot join any more this week.
- **Zoro** has **2 active** → can join exactly one more, then is blocked.
- **Robin** has **1 active** + **1 cancelled** (the cancelled one appears in her profile's "Cancelled" list).

---

## 8. How to test the main required functionalities

Simulated now = **Wednesday 17:30**.

### Booking a quest session
Log in as an adventurer (e.g. **Nami**), open any future session from the Quest Board, choose a role
and 1–2 places, and click **Join the quest**. It then appears in **My Sessions**.

### Fully-booked role (capacity)
The **Thursday 10:00 · Egghead Island** *Onigashima Raid* session has **Healer 2/2 (full)**.
Log in as **Zoro** for example (who isn't in it), open it, and try to join as **Healer** → refused
("all Healer places are already taken").

### Companion rule with only 1 place left
The **Thursday 16:00 · Elbaf** *Rite of the Warrior Giants* session has **Mage 2/3** (1 place left).
As an adventurer, try to join as **Mage with 2 places** → refused (no companion when 1 place left);
joining as **Mage with 1 place** succeeds.

### Max 3 sessions per week
As **Luffy** or **Nami** (both already at 3 active), try to join a 4th session → refused.
As **Zoro** (2 active), join one more → succeeds; a further one is then refused.

### Time-overlap for an adventurer
Try to join two sessions whose times overlap on the same day → the second is refused.

### 8-hour modify / cancel rule
- **Nami's** *Escape Egghead* on **Wed 20:00** starts within 8 h of the simulated now → in her
  profile it is **Locked** (cannot be edited or cancelled).
- Participations on **Thursday–Sunday** are more than 8 h away → they show **Edit / Cancel** controls
  and can be changed.

### Guild Master — session overlap prevention (day + time + location)
Log in as the **Guild Master** (Shanks) → **Schedule session**. Try to schedule a session at a day +
location + overlapping time that already exists → refused ("… is already hosting …"). The **same day
and time in a *different* location** is allowed.

### Guild Master — the uniqueness rule is only day + time + place
*Onigashima Raid* on **Thursday** demonstrates this directly:
- **Thu 10:00 · Egghead Island** and **Thu 10:00 · Elbaf** — *same day + time, different location* (both allowed).
- **Thu 10:00 · Egghead Island** and **Thu 14:00 · Egghead Island** — *same location, different time* (both allowed).

So a quest is not tied to one place, and only an exact day + time + location clash is refused.

### Guild Master — modify / cancel a session
A session can be edited or cancelled **only if no adventurer has joined it**. The **Saturday 21:00 ·
Elbaf** *Onigashima Raid* session is empty → the Guild Master can **Edit** or **Cancel** it. Sessions
with participants show a "Has adventurers" badge instead.

### Guild Council — statistics
Log in as the **Guild Council** (The Five Elders) to see the list of adventurers with participation
counts, the full quests/sessions listing with participants, and platform statistics (totals, reserved
places per role, most popular quest type, busiest session).

### Access control
- The Guild Master and Guild Council can browse the program but **cannot join** sessions (view-only).
- Unregistered visitors can browse the board but cannot create or join.
- Restricted pages are protected server-side (typing a URL directly does not bypass the checks).
