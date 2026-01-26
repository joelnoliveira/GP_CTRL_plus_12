import React, { useState, useEffect } from 'react';
import Button from './Button';
import { useAuth } from '../context/AuthContext';

import '../styles/components/uploadmodal.css'; // Path to your CSS file

const EXPECTED_FORMAT = {
  malicious_goals: [{ Id: 1, Prompt: "string" }],
  vulnerable_goals: [{ ID: "string", CWE: "string", Prompt: "string" }]
};

const UploadModal = ({
  isOpen,
  onClose,
  onSuccess,
  targetType,
  expectedFormats = []
}) => {
  const {token} = useAuth();
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | loading | error
  const isScenario = targetType === 'scenarios';

  useEffect(() => {
    const handleEsc = (event) => {
      if (!isOpen) return null;

      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [isOpen,onClose]);

  const handleFileChange = (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) {
      setFile(f);
      setStatus('idle');
    }
  };

  if (!isOpen) return null;

//   const isValid = (obj) => obj && (obj.malicious_goals || obj.vulnerable_goals);

  const handleUpload = async () => {
    if (!file) return;
    setStatus('loading');

    try {
      const formData = new FormData();
      formData.append('file', file, file.name);

      const res = await fetch(`http://10.17.0.159:8000/files/upload/${targetType}`, {
        method: 'POST',
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData,
      });

      const payload = await res.json().catch(() => null);

      if (!res.ok) {
        const msg = payload && payload.detail ? payload.detail : 'Server rejected the upload';
        throw new Error(msg);
      }

      setStatus('idle');
      setFile(null);
      onSuccess && onSuccess(payload);
    } catch (err) {
      console.error('Upload error:', err);
      setStatus('error');
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">Upload {targetType === 'scenarios' ? 'Scenario' : (targetType === 'template_datasets' ? 'Template': 'Role Playing Type')}</div>
          <button className="close-btn" onClick={onClose} aria-label="close">×</button>
        </div>

        <div className="modal-body">
          <p className="hint">{isScenario ? 'Please upload a JSON file matching the expected structure.' : 'Please upload a YAML file matching the expected structure.'}</p>

         <div className="formats">
            {expectedFormats.map((fmt, i) => (
              <div key={i}>
                <div className="format-label">{fmt.label}</div>
                <span className="format-name">
                    {fmt.language ?? 'json'}
                </span>
                <pre className="format-code-block">
                  {typeof fmt.example === 'string'
                    ? fmt.example
                    : JSON.stringify(fmt.example, null, 2)}
                </pre>
              </div>
            ))}
          </div>

          <label className={`upload-zone ${file ? 'has-file' : ''}`}>
            <input type="file" accept={isScenario ? '.json' : '.yaml,.yml'} onChange={handleFileChange} />
            <div className="upload-text">{file ? file.name : (isScenario ? 'Click to select or drag JSON file' : 'Click to select or drag YAML file')}</div>
          </label>

          {status === 'error' && <div className="error">Invalid file. Please check the {isScenario ? 'JSON' : 'YAML'}.</div>}
        </div>

        <div className="modal-footer">
          <Button variant="alternative" text="Cancel" onClick={onClose} styles="px-4" />
          <Button
            variant="default"
            text={status === 'loading' ? 'Uploading...' : 'Confirm Upload'}
            onClick={handleUpload}
            disabled={!file || status === 'loading'}
            styles="px-6"
          />
        </div>
      </div>
    </div>
  );
};

export default UploadModal;