import React from 'react';

export default function LoginPage() {
  return (
    <div>
      <h1>登录</h1>
      <form>
        <div>
          <label htmlFor="emailOrUsername">邮箱或用户名</label>
          <input type="text" id="emailOrUsername" name="emailOrUsername" />
        </div>
        <div>
          <label htmlFor="password">密码</label>
          <input type="password" id="password" name="password" />
        </div>
        <button type="submit">登录</button>
      </form>
    </div>
  );
}