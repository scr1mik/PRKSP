import { useEffect, useState } from "react";

import {
  createEvent,
  deleteEvent,
  fetchCurrentUser,
  fetchEvents,
  fetchRelease,
  loginUser,
  logoutUser,
  registerUser,
  updateEvent,
} from "./api";
import "./styles.css";

const emptyForm = {
  title: "",
  description: "",
  year: new Date().getFullYear(),
  category: "",
};

const emptyAuthForm = {
  email: "",
  password: "",
  full_name: "",
};

function App() {
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [authForm, setAuthForm] = useState(emptyAuthForm);
  const [currentUser, setCurrentUser] = useState(null);
  const [release, setRelease] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Загрузка событий...");
  const [authMessage, setAuthMessage] = useState("Войдите или создайте пользователя");

  useEffect(() => {
    loadEvents();
    loadCurrentUser();
    loadRelease();
  }, []);

  async function loadEvents() {
    try {
      const data = await fetchEvents();
      setEvents(data);
      setStatusMessage(data.length ? "События загружены" : "Список событий пока пуст");
    } catch (error) {
      console.error(error);
      setStatusMessage("Не удалось загрузить события");
    }
  }

  async function loadCurrentUser() {
    try {
      const user = await fetchCurrentUser();
      setCurrentUser(user);
      setAuthMessage(`Активная сессия: ${user.email}`);
    } catch {
      setCurrentUser(null);
    }
  }

  async function loadRelease() {
    try {
      setRelease(await fetchRelease());
    } catch (error) {
      console.error(error);
    }
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name === "year" ? Number(value) : value,
    }));
  }

  function handleAuthChange(event) {
    const { name, value } = event.target;
    setAuthForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleRegister(event) {
    event.preventDefault();

    try {
      await registerUser(authForm);
      setAuthMessage("Пользователь создан, теперь можно войти");
    } catch (error) {
      console.error(error);
      setAuthMessage("Не удалось зарегистрировать пользователя");
    }
  }

  async function handleLogin(event) {
    event.preventDefault();

    try {
      const user = await loginUser({
        email: authForm.email,
        password: authForm.password,
      });
      setCurrentUser(user);
      setAuthForm(emptyAuthForm);
      setAuthMessage(`Активная сессия: ${user.email}`);
    } catch (error) {
      console.error(error);
      setAuthMessage("Не удалось войти");
    }
  }

  async function handleLogout() {
    try {
      await logoutUser();
      setCurrentUser(null);
      setAuthMessage("Сессия завершена");
    } catch (error) {
      console.error(error);
      setAuthMessage("Не удалось завершить сессию");
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      if (editingId === null) {
        await createEvent(form);
        setStatusMessage("Событие добавлено");
      } else {
        await updateEvent(editingId, form);
        setStatusMessage("Событие обновлено");
      }

      setForm(emptyForm);
      setEditingId(null);
      await loadEvents();
    } catch (error) {
      console.error(error);
      setStatusMessage("Не удалось сохранить событие");
    }
  }

  function handleEdit(item) {
    setEditingId(item.id);
    setForm({
      title: item.title,
      description: item.description,
      year: item.year,
      category: item.category,
    });
    setStatusMessage(`Редактирование: ${item.title}`);
  }

  async function handleDelete(eventId) {
    try {
      await deleteEvent(eventId);
      setStatusMessage("Событие удалено");
      if (editingId === eventId) {
        setForm(emptyForm);
        setEditingId(null);
      }
      await loadEvents();
    } catch (error) {
      console.error(error);
      setStatusMessage("Не удалось удалить событие");
    }
  }

  return (
    <div className="page">
      <main className="layout">
        <section className="hero">
          <p className="eyebrow">САЙТ СОЗДАЛ ДМИТРИЙ УТКИН</p>
          <h1>МИРОВЫЕ ИВЕНТЫ</h1>
          <p className="hero-text">
            Каталог гипотетических событий будущего: от новой пандемии до вторжения
            инопланетян.
          </p>
          {release && (
            <p className="release">
              {release.environment} · {release.image_tag} · {release.release_id}
            </p>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Пользовательская сессия</h2>
            <span>{authMessage}</span>
          </div>

          {currentUser ? (
            <div className="session-box">
              <strong>{currentUser.full_name}</strong>
              <span>{currentUser.email}</span>
              <button type="button" className="secondary" onClick={handleLogout}>
                Выйти
              </button>
            </div>
          ) : (
            <form className="event-form" onSubmit={handleLogin}>
              <input
                name="email"
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={handleAuthChange}
                required
              />
              <input
                name="password"
                type="password"
                placeholder="Пароль"
                value={authForm.password}
                onChange={handleAuthChange}
                required
              />
              <input
                name="full_name"
                placeholder="Имя для регистрации"
                value={authForm.full_name}
                onChange={handleAuthChange}
              />
              <div className="actions">
                <button type="submit">Войти</button>
                <button type="button" className="secondary" onClick={handleRegister}>
                  Зарегистрироваться
                </button>
              </div>
            </form>
          )}
        </section>

        <section className="panel">
          <h2>{editingId === null ? "Добавить событие" : "Редактировать событие"}</h2>
          <form className="event-form" onSubmit={handleSubmit}>
            <input
              name="title"
              placeholder="Название события"
              value={form.title}
              onChange={handleChange}
              required
            />
            <textarea
              name="description"
              placeholder="Краткое описание"
              value={form.description}
              onChange={handleChange}
              rows="4"
              required
            />
            <div className="grid">
              <input
                name="year"
                type="number"
                min="2024"
                max="9999"
                value={form.year}
                onChange={handleChange}
                required
              />
              <input
                name="category"
                placeholder="Категория"
                value={form.category}
                onChange={handleChange}
                required
              />
            </div>
            <div className="actions">
              <button type="submit">
                {editingId === null ? "Добавить" : "Сохранить"}
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setForm(emptyForm);
                  setEditingId(null);
                }}
              >
                Сбросить
              </button>
            </div>
          </form>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Список событий</h2>
            <span>{statusMessage}</span>
          </div>

          <div className="cards">
            {events.map((item) => (
              <article className="card" key={item.id}>
                <div className="card-meta">
                  <span>{item.category}</span>
                  <strong>{item.year}</strong>
                </div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <div className="actions">
                  <button type="button" onClick={() => handleEdit(item)}>
                    Изменить
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={() => handleDelete(item.id)}
                  >
                    Удалить
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
