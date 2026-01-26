import React, { useState } from "react";
import "../styles/pages/external_apis.css";
import { useAuth } from '../context/AuthContext';
import Menu from '../components/Menu';
import Button from "../components/Button";
import Toast from "../components/Toast";
import ApiConfigModal from "../components/ApiConfigModal";
import { useApiConfigs } from "../hooks/useApiConfigs";

const ExternalApis = () => {
    const { isLoggedIn } = useAuth();
    const { apiConfigs, isLoading, createConfig, updateConfig, deleteConfig } = useApiConfigs();

    const [toastConfig, setToastConfig] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingConfig, setEditingConfig] = useState(null);

    const handleAddNew = () => {
        setEditingConfig(null);
        setIsModalOpen(true);
    };

    const handleEdit = (config) => {
        setEditingConfig(config);
        setIsModalOpen(true);
    };

    const handleDelete = async (configId) => {
        if (!window.confirm('Are you sure you want to delete this API configuration?')) {
            return;
        }

        const result = await deleteConfig(configId);
        if (result.success) {
            setToastConfig({ type: "success", message: "API configuration deleted successfully!" });
        } else {
            setToastConfig({ type: "error", message: result.error || "Failed to delete configuration" });
        }
    };

    const handleSave = async (formData) => {
        let result;
        if (editingConfig) {
            result = await updateConfig(editingConfig.id, formData);
        } else {
            result = await createConfig(formData);
        }

        if (result.success) {
            setToastConfig({
                type: "success",
                message: editingConfig
                    ? "API configuration updated successfully!"
                    : "API configuration created successfully!"
            });
            return { success: true };
        } else {
            return { success: false, error: result.error };
        }
    };

    return (
        <div className="external_apis">
            <Menu currentPage={"External APIs"} />

            {toastConfig && (
                <Toast
                    icon_size="large"
                    type={toastConfig.type}
                    message={toastConfig.message}
                    onClose={() => setToastConfig(null)}
                />
            )}

            <ApiConfigModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSave}
                initialData={editingConfig}
                isLoading={isLoading}
            />

            <div className="external_apis__main_area">
                <div className="external_apis__card-wrapper">
                    <div className="external_apis__card">
                        <div className="external_apis__header">
                            <h1 className="external_apis__title">External APIs</h1>
                            <Button
                                onClick={handleAddNew}
                                type="button"
                                variant="default"
                                size="small"
                                text="+ Add API"
                                disabled={!isLoggedIn}
                            />
                        </div>

                        <div className="external_apis__list">
                            {isLoading && apiConfigs.length === 0 ? (
                                <div className="external_apis__empty">Loading...</div>
                            ) : apiConfigs.length === 0 ? (
                                <div className="external_apis__empty">
                                    No API configurations yet. Click "Add API" to create one.
                                </div>
                            ) : (
                                apiConfigs.map((config) => (
                                    <div key={config.id} className="external_apis__item">
                                        <div className="external_apis__item-info">
                                            <span className="external_apis__item-name">{config.name}</span>
                                            <span className="external_apis__item-provider">{config.provider}</span>
                                            {config.api_key_masked && (
                                                <span className="external_apis__item-key">{config.api_key_masked}</span>
                                            )}
                                        </div>
                                        <div className="external_apis__item-actions">
                                            <button
                                                className="external_apis__action-btn external_apis__action-btn--edit"
                                                onClick={() => handleEdit(config)}
                                            >
                                                Edit
                                            </button>
                                            <button
                                                className="external_apis__action-btn external_apis__action-btn--delete"
                                                onClick={() => handleDelete(config.id)}
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div
                className="home__gray-polygon -z-5"
                style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
            ></div>
        </div>
    );
};

export default ExternalApis;
