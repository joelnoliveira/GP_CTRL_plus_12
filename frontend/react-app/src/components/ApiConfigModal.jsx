import React, { useState, useEffect } from 'react';
import Button from './Button';
import { PROVIDERS } from '../hooks/useApiConfigs';

import '../styles/components/api_config_modal.css';

const ApiConfigModal = ({
    isOpen,
    onClose,
    onSave,
    initialData = null,
    isLoading = false,
}) => {
    const [formData, setFormData] = useState({
        name: '',
        provider: 'OPEN_AI',
        api_key: '',
    });
    const [error, setError] = useState('');

    useEffect(() => {
        if (initialData) {
            setFormData({
                name: initialData.name || '',
                provider: initialData.provider || 'OPEN_AI',
                api_key: '', // Don't pre-fill API key for security
            });
        } else {
            setFormData({
                name: '',
                provider: 'OPEN_AI',
                api_key: '',
            });
        }
        setError('');
    }, [initialData, isOpen]);

    useEffect(() => {
        const handleEsc = (event) => {
            if (!isOpen) return;
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('keydown', handleEsc);
        return () => document.removeEventListener('keydown', handleEsc);
    }, [isOpen, onClose]);

    const handleChange = (field) => (e) => {
        setFormData(prev => ({
            ...prev,
            [field]: e.target.value
        }));
        setError('');
    };

    const handleSubmit = async () => {
        if (!formData.name.trim()) {
            setError('Name is required');
            return;
        }
        if (!formData.api_key.trim() && !initialData) {
            setError('API Key is required');
            return;
        }

        const result = await onSave({
            ...formData,
            model_name: null, // Explicitly send null
            api_key: formData.api_key.trim() || (initialData?.api_key || ''),
        });

        if (result?.success) {
            onClose();
        } else if (result?.error) {
            setError(result.error);
        }
    };

    if (!isOpen) return null;

    const isEditing = !!initialData;

    return (
        <div className="api_config_modal__backdrop" onClick={onClose}>
            <div className="api_config_modal__container" onClick={(e) => e.stopPropagation()}>
                <div className="api_config_modal__header">
                    <h2 className="api_config_modal__title">
                        {isEditing ? 'Edit API Configuration' : 'Add API Configuration'}
                    </h2>
                    <button className="api_config_modal__close" onClick={onClose} aria-label="close">
                        ×
                    </button>
                </div>

                <div className="api_config_modal__form">
                    <div className="api_config_modal__field">
                        <label className="api_config_modal__label">Name</label>
                        <input
                            type="text"
                            className="api_config_modal__input"
                            placeholder="My OpenAI API"
                            value={formData.name}
                            onChange={handleChange('name')}
                        />
                    </div>

                    <div className="api_config_modal__field">
                        <label className="api_config_modal__label">Provider</label>
                        <select
                            className="api_config_modal__select"
                            value={formData.provider}
                            onChange={handleChange('provider')}
                        >
                            {PROVIDERS.map(p => (
                                <option key={p.key} value={p.key}>{p.label}</option>
                            ))}
                        </select>
                    </div>

                    <div className="api_config_modal__field">
                        <label className="api_config_modal__label">
                            API Key {isEditing && '(leave blank to keep current)'}
                        </label>
                        <input
                            type="password"
                            className="api_config_modal__input"
                            placeholder={isEditing ? '••••••••' : 'sk-...'}
                            value={formData.api_key}
                            onChange={handleChange('api_key')}
                        />
                        <div className="api_config_modal__warning">
                            ⚠️ Warning: Executing attacks with your own API Key carries a risk of your account being banned by the provider.
                        </div>
                    </div>

                    {error && <div className="api_config_modal__error">{error}</div>}
                </div>

                <div className="api_config_modal__footer">
                    <Button variant="alternative" text="Cancel" onClick={onClose} styles="px-4" />
                    <Button
                        variant="default"
                        text={isLoading ? 'Saving...' : 'Save'}
                        onClick={handleSubmit}
                        disabled={isLoading}
                        styles="px-6"
                    />
                </div>
            </div>
        </div>
    );
};

export default ApiConfigModal;
