import React, { useState } from 'react'

import { useAuth } from "../context/AuthContext";

import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import RunCard from '../components/RunCard'

import useHistoryFilters from "../hooks/useHistoryFilters";
import useHistoryRuns from "../hooks/useHistoryRuns";

import "../styles/pages/history.css"

const History = (
) => {
  const { isLoggedIn, user } = useAuth();

  const { filters } = useHistoryFilters();

  const [selectedFilters, setSelectedFilters] = useState({});

  const { runs, loading, error } = useHistoryRuns(selectedFilters);

  return (
    <div className="history-page">
      <Menu 
        currentPage={"History"}
      />

      <div className="history-page__content">

        <div className="history-page__filter-container">
          {loading && <p>Loading filters...</p>}
          {error && <p className="text-red-500">{error}</p>}

          {!loading &&
            !error &&
            filters.map((filter, index) => (
              <DropdownMenu
                key={index}
                placeholder={filter.placeholder}
                items={filter.items}
                value={selectedFilters[filter.key]}
                onSelect={(value) =>
                  setSelectedFilters(prev => ({
                    ...prev,
                    [filter.key]: value,
                  }))
                }
              />
            ))}
        </div>

        <div className="history-page__runs-container">
          {
            !isLoggedIn ? (
              runs.map((run, index) => (
                <RunCard 
                  key={index}
                  run_name_id={run.run_name_id}
                  username={run.username}
                  attack_type={run.attack_type}
                  date={run.date}
                  status={run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                  attack_model={run.attack_model}
                  target_model={run.target_model}
                  isPublicValue={run.isPublicValue}
                  canChangeStatus={false}
                />
              ))
            ):
            (
              runs.map((run, index) => (
                <RunCard 
                  key={index}
                  run_name_id={run.run_name_id}
                  username={run.username}
                  attack_type={run.attack_type}
                  date={run.date}
                  status={run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                  attack_model={run.attack_model}
                  target_model={run.target_model}
                  isPublicValue={run.isPublicValue}
                  canChangeStatus={user ? user.username === run.username : false}
                />
              ))
            )
          }
        </div>
        
      </div>
      
    </div>
  )
}

export default History