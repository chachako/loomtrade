"use client";

import React, { useState } from 'react';

// 模拟的配置数据接口
interface ApiKeyConfig {
  id: string;
  marketType: 'crypto' | 'stock' | 'forex';
  exchangeName: string;
  apiKeySet: boolean;
  secretKeySet: boolean;
  // 更多字段可以根据需要添加
}

// 模拟的现有配置数据
const mockConfigs: ApiKeyConfig[] = [
  { id: '1', marketType: 'crypto', exchangeName: 'Binance', apiKeySet: true, secretKeySet: true },
  { id: '2', marketType: 'stock', exchangeName: 'TD Ameritrade', apiKeySet: true, secretKeySet: false },
  { id: '3', marketType: 'forex', exchangeName: 'OANDA', apiKeySet: false, secretKeySet: false },
];

const ApiKeysPage = () => {
  const [configs, setConfigs] = useState<ApiKeyConfig[]>(mockConfigs);
  const [newMarketType, setNewMarketType] = useState<'crypto' | 'stock' | 'forex'>('crypto');
  const [newExchangeName, setNewExchangeName] = useState('');
  const [newApiKey, setNewApiKey] = useState('');
  const [newSecretKey, setNewSecretKey] = useState('');
  const [newPassphrase, setNewPassphrase] = useState('');
  const [newPermissions, setNewPermissions] = useState('');

  const handleAddConfig = (e: React.FormEvent) => {
    e.preventDefault();
    // 在实际应用中，这里会调用 API
    console.log('Adding new config:', {
      marketType: newMarketType,
      exchangeName: newExchangeName,
      apiKey: newApiKey,
      secretKey: newSecretKey,
      passphrase: newPassphrase,
      permissions: newPermissions,
    });
    // 清空表单或给出反馈
    setNewExchangeName('');
    setNewApiKey('');
    setNewSecretKey('');
    setNewPassphrase('');
    setNewPermissions('');
    // 实际应用中会刷新列表
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">交易市场 API Key 配置</h1>

      {/* 配置列表 */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">现有配置</h2>
        {configs.length === 0 ? (
          <p>暂无配置。</p>
        ) : (
          <ul className="space-y-4">
            {configs.map((config) => (
              <li key={config.id} className="p-4 border rounded-lg shadow-sm bg-white">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-medium">{config.exchangeName} ({config.marketType.toUpperCase()})</h3>
                    <p className="text-sm text-gray-600">
                      API Key: {config.apiKeySet ? <span className="text-green-500">已设置</span> : <span className="text-red-500">未设置</span>}
                    </p>
                    <p className="text-sm text-gray-600">
                      Secret Key: {config.secretKeySet ? <span className="text-green-500">已设置</span> : <span className="text-red-500">未设置</span>}
                    </p>
                  </div>
                  <div className="space-x-2">
                    <button className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600">编辑</button>
                    <button className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600">删除</button>
                    <button className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600">测试连接</button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* 添加配置表单 */}
      <div className="p-6 border rounded-lg shadow-sm bg-white">
        <h2 className="text-xl font-semibold mb-4">添加新配置</h2>
        <form onSubmit={handleAddConfig} className="space-y-4">
          <div>
            <label htmlFor="marketType" className="block text-sm font-medium text-gray-700">市场类型</label>
            <select
              id="marketType"
              value={newMarketType}
              onChange={(e) => setNewMarketType(e.target.value as 'crypto' | 'stock' | 'forex')}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="crypto">加密货币 (Crypto)</option>
              <option value="stock">股票 (Stock)</option>
              <option value="forex">外汇 (Forex)</option>
            </select>
          </div>
          <div>
            <label htmlFor="exchangeName" className="block text-sm font-medium text-gray-700">交易所/经纪商名称</label>
            <input
              type="text"
              id="exchangeName"
              value={newExchangeName}
              onChange={(e) => setNewExchangeName(e.target.value)}
              required
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700">API Key</label>
            <input
              type="text"
              id="apiKey"
              value={newApiKey}
              onChange={(e) => setNewApiKey(e.target.value)}
              required
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="secretKey" className="block text-sm font-medium text-gray-700">Secret Key</label>
            <input
              type="password"
              id="secretKey"
              value={newSecretKey}
              onChange={(e) => setNewSecretKey(e.target.value)}
              required
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="passphrase" className="block text-sm font-medium text-gray-700">Passphrase (可选)</label>
            <input
              type="password"
              id="passphrase"
              value={newPassphrase}
              onChange={(e) => setNewPassphrase(e.target.value)}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="permissions" className="block text-sm font-medium text-gray-700">权限说明/范围 (可选)</label>
            <input
              type="text"
              id="permissions"
              value={newPermissions}
              onChange={(e) => setNewPermissions(e.target.value)}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="例如: read-only, trade"
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 bg-indigo-600 text-white font-semibold rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            添加配置
          </button>
        </form>
      </div>
    </div>
  );
};

export default ApiKeysPage;