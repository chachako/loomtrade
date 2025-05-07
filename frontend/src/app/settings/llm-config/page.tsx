'use client';

import React, { useState } from 'react';

interface LLMConfig {
  id: string;
  providerName: string;
  modelName: string;
  apiKeySet: boolean;
}

const LLMConfigPage = () => {
  // Mock data for existing configurations
  const [configs, setConfigs] = useState<LLMConfig[]>([
    { id: '1', providerName: 'OpenAI', modelName: 'gpt-4-turbo', apiKeySet: true },
    { id: '2', providerName: 'Anthropic', modelName: 'claude-3-opus', apiKeySet: false },
  ]);

  // State for the new config form
  const [newProviderName, setNewProviderName] = useState('OpenAI');
  const [newModelName, setNewModelName] = useState('');
  const [newApiKey, setNewApiKey] = useState('');

  const handleAddConfig = (event: React.FormEvent) => {
    event.preventDefault();
    // Placeholder for actual add logic
    console.log('Adding new config:', { provider: newProviderName, model: newModelName, apiKey: newApiKey.substring(0, 5) + '...' });
    // Clear form
    setNewModelName('');
    setNewApiKey('');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>LLM Provider 配置</h1>

      <section style={{ marginBottom: '30px' }}>
        <h2>现有配置</h2>
        {configs.length === 0 ? (
          <p>暂无配置。</p>
        ) : (
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {configs.map((config) => (
              <li key={config.id} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong>Provider:</strong> {config.providerName} <br />
                  <strong>模型:</strong> {config.modelName} <br />
                  <strong>API Key:</strong> {config.apiKeySet ? <span style={{ color: 'green' }}>已设置</span> : <span style={{ color: 'red' }}>未设置</span>}
                </div>
                <div>
                  <button style={{ marginRight: '5px' }}>编辑</button>
                  <button>删除</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>添加新配置</h2>
        <form onSubmit={handleAddConfig} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
          <div>
            <label htmlFor="providerName" style={{ display: 'block', marginBottom: '5px' }}>Provider 名称:</label>
            <select
              id="providerName"
              value={newProviderName}
              onChange={(e) => setNewProviderName(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            >
              <option value="OpenAI">OpenAI</option>
              <option value="Anthropic">Anthropic</option>
              {/* Add other providers as needed */}
            </select>
          </div>
          <div>
            <label htmlFor="modelName" style={{ display: 'block', marginBottom: '5px' }}>模型名称:</label>
            <input
              type="text"
              id="modelName"
              value={newModelName}
              onChange={(e) => setNewModelName(e.target.value)}
              placeholder="例如: gpt-4-turbo, claude-3-sonnet"
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            />
          </div>
          <div>
            <label htmlFor="apiKey" style={{ display: 'block', marginBottom: '5px' }}>API Key:</label>
            <input
              type="password"
              id="apiKey"
              value={newApiKey}
              onChange={(e) => setNewApiKey(e.target.value)}
              placeholder="输入您的 API Key"
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
            />
          </div>
          <button type="submit" style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            添加配置
          </button>
        </form>
      </section>
    </div>
  );
};

export default LLMConfigPage;