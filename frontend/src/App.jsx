import { useEffect, useState } from "react";

import { createEvent, deleteEvent, fetchEvents, updateEvent } from "./api";
import "./styles.css";

const emptyForm = {
  title: "",
  description: "",
  year: new Date().getFullYear(),
  category: "",
};

function App() {
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [statusMessage, setStatusMessage] = useState("Загрузка событий...");

  useEffect(() => {
    loadEvents();
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

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name === "year" ? Number(value) : value,
    }));
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
