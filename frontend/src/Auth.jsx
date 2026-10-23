import { useState } from "react";
import { Icon } from "./App";
import { apiRequest, saveTokens } from "./api";

export default function Auth({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const credentials = { email: form.email, password: form.password };
      if (mode === "register") {
        await apiRequest("/auth/register/", {
          method: "POST",
          body: { ...credentials, username: form.name },
          auth: false,
        });
      }

      const tokens = await apiRequest("/auth/login/", {
        method: "POST",
        body: credentials,
        auth: false,
      });
      saveTokens(tokens);
      onSuccess({ email: form.email, username: form.name || form.email.split("@")[0] });
    } catch (requestError) {
      setError(requestError.message || "Проверьте введённые данные");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-story">
        <div className="auth-brand">
          <span className="brand-mark"><Icon name="sprout" size={28} /></span>
          <span>EcoPet <b>Planner</b></span>
        </div>
        <div>
          <span className="eyebrow light">ПАМЯТЬ, КОТОРАЯ РАСТЁТ</span>
          <h1>Пусть любовь<br />продолжает жить</h1>
          <p>Создайте живой мемориал, который станет частью природы и сохранит тёплую память на долгие годы.</p>
        </div>
        <div className="auth-note"><Icon name="leaf" /> Экологично и с заботой о будущем</div>
      </section>

      <section className="auth-form-wrap">
        <div className="auth-card">
          <span className="eyebrow">ДОБРО ПОЖАЛОВАТЬ</span>
          <h2>{mode === "login" ? "Войдите в свой сад" : "Создайте свой сад"}</h2>
          <p>{mode === "login" ? "Продолжите заботиться о живой памяти." : "Начните путь к светлой и живой памяти."}</p>

          <div className="auth-tabs">
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Вход</button>
            <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Регистрация</button>
          </div>

          <form onSubmit={submit}>
            {mode === "register" && (
              <label>Ваше имя<input name="name" value={form.name} onChange={update} placeholder="Как к вам обращаться?" required /></label>
            )}
            <label>Электронная почта<input type="email" name="email" value={form.email} onChange={update} placeholder="name@example.ru" required /></label>
            <label>Пароль<input type="password" name="password" value={form.password} onChange={update} placeholder="Не менее 8 символов" minLength="8" required /></label>
            {error && <p className="form-error">{error}</p>}
            <button className="primary-button full" disabled={loading}>
              {loading ? <span className="loader" /> : mode === "login" ? "Войти" : "Создать аккаунт"}
              {!loading && <Icon name="arrow" />}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
