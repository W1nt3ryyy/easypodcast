import React, { useEffect, useMemo, useRef, useState } from 'react';
import './index.css';
import { I18nProvider, useI18n } from './i18n';

const IconHome = () => <svg className="icon" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>;
const IconRSS = () => <svg className="icon" viewBox="0 0 24 24"><path d="M6.18 15.64a2.18 2.18 0 1 1 0 4.36 2.18 2.18 0 0 1 0-4.36M4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44m0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1z"/></svg>;
const IconPlay = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>;
const IconPause = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h4v14H6zm8 0h4v14h-4z"/></svg>;
const IconBack = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>;
const IconSun = () => <svg className="icon" viewBox="0 0 24 24"><path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10M2 13h2a1 1 0 0 0 0-2H2a1 1 0 0 0 0 2m18 0h2a1 1 0 0 0 0-2h-2a1 1 0 0 0 0 2M11 2v2a1 1 0 0 0 2 0V2a1 1 0 0 0-2 0m0 18v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-2 0z"/></svg>;
const IconMoon = () => <svg className="icon" viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.4 5.4 0 0 1-9.8-3.14c0-1.81.89-3.42 2.26-4.4A9 9 0 0 0 12 3z"/></svg>;
const IconSearch = () => <svg className="icon" viewBox="0 0 24 24"><path d="M9.5 3a6.5 6.5 0 0 1 5.16 10.45l4.45 4.44-1.42 1.42-4.44-4.45A6.5 6.5 0 1 1 9.5 3m0 2a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9z"/></svg>;
const IconUser = () => <svg className="icon" viewBox="0 0 24 24"><path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10m0 2c-3.33 0-10 1.67-10 5v3h20v-3c0-3.33-6.67-5-10-5z"/></svg>;
const IconCheck = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="m9 16.17-3.88-3.88L3.7 13.7 9 19 21 7l-1.41-1.41z"/></svg>;
const IconShuffle = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M10.59 9.17 5.41 4 4 5.41l5.17 5.18 1.42-1.42M14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5m.33 9.41-1.42 1.42 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/></svg>;
const IconPrev = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M7 6h2v12H7V6m4 6 7-5v10l-7-5z"/></svg>;
const IconNext = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M15 6h2v12h-2V6M6 7l7 5-7 5V7z"/></svg>;
const IconRepeat = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M7 7h11v3l4-4-4-4v3H5v6h2V7m10 10H6v-3l-4 4 4 4v-3h13v-6h-2v4z"/></svg>;
const IconVolume = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3m13.5 3A4.5 4.5 0 0 0 14 7.97v8.05A4.47 4.47 0 0 0 16.5 12M14 3.23v2.06a7 7 0 0 1 0 13.42v2.06A9 9 0 0 0 14 3.23z"/></svg>;
const IconClose = () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>;

const browseGenres = [
  ['all', 'Все'],
  ['technology', 'Technology'],
  ['news', 'News'],
  ['religion', 'Religion & Spirituality'],
  ['education', 'Education'],
  ['business', 'Business'],
  ['comedy', 'Comedy'],
  ['science', 'Science'],
];

function SkeletonCard() {
  return <div className="podcast-card skeleton"><div className="skeleton-content"><div className="skeleton-title"></div><div className="skeleton-author"></div><div className="skeleton-bottom"><div className="skeleton-btn"></div><div className="skeleton-avatar"></div></div></div></div>;
}

function SkeletonEpisode() {
  return <div className="ep-item skeleton"><div className="skeleton-cover"></div><div className="skeleton-details"><div className="skeleton-ep-title"></div><div className="skeleton-ep-meta"></div></div></div>;
}

function AppContent() {
  const { t, formatDate } = useI18n();
  const [podcasts, setPodcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [theme, setTheme] = useState(() => document.cookie.match(/theme=(light|dark)/)?.[1] || 'light');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPodcast, setSelectedPodcast] = useState(null);
  const [podcastDetails, setPodcastDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [episodesLoadingMore, setEpisodesLoadingMore] = useState(false);
  const [currentEpisode, setCurrentEpisode] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [position, setPosition] = useState(0);
  const [volume, setVolume] = useState(0.9);
  const [shuffleEnabled, setShuffleEnabled] = useState(false);
  const [repeatEnabled, setRepeatEnabled] = useState(false);
  const [token, setToken] = useState(() => localStorage.getItem('jwt') || '');
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ username: '', email: '', password: '' });
  const [profileForm, setProfileForm] = useState({ username: '', email: '', password: '' });
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [browseGenre, setBrowseGenre] = useState('all');
  const [browseResults, setBrowseResults] = useState([]);
  const [browseCache, setBrowseCache] = useState({});
  const [browseLoading, setBrowseLoading] = useState(false);
  const [rssModalOpen, setRssModalOpen] = useState(false);
  const [rssUrl, setRssUrl] = useState('');
  const [notice, setNotice] = useState(null);
  const [useDirectAudio, setUseDirectAudio] = useState(false);
  const audioRef = useRef(null);
  const noticeTimerRef = useRef(null);

  const classes = ['c-pink', 'c-blue', 'c-purple', 'c-green'];
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const apiFetch = (url, options = {}) => fetch(url, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...authHeaders,
      ...(options.headers || {}),
    },
  });

  const readJsonResponse = async (response) => {
    const text = await response.text();
    if (!text) throw new Error('Сервер не вернул ответ. Проверьте API-контейнер.');
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error('Сервер вернул неожиданный ответ. Проверьте Docker-прокси API.');
    }
    if (!response.ok) throw new Error(data.error || 'Запрос не выполнен');
    return data;
  };

  const showNotice = (message, title = 'Готово') => {
    setNotice({ title, message });
    window.clearTimeout(noticeTimerRef.current);
    noticeTimerRef.current = window.setTimeout(() => setNotice(null), 2800);
  };

  const loadPodcasts = () => {
    setLoading(true);
    apiFetch('/api/podcasts/')
      .then(readJsonResponse)
      .then(data => data.status === 'ok' && setPodcasts(data.items))
      .catch(e => console.error('Error fetching podcasts:', e))
      .finally(() => setLoading(false));
  };

  const loadHistory = () => {
    if (!token) {
      setHistory([]);
      return;
    }
    apiFetch('/api/podcasts/history/')
      .then(readJsonResponse)
      .then(data => data.status === 'ok' && setHistory(data.items))
      .catch(() => setHistory([]));
  };

  function saveProgress(episode = currentEpisode, currentTime = audioRef.current?.currentTime || 0, totalDuration = audioRef.current?.duration || duration || episode?.duration || 0) {
    if (!episode?.url) return Promise.resolve();
    apiFetch('/api/podcasts/progress/save/', {
      method: 'POST',
      body: JSON.stringify({
        episode_url: episode.url,
        current_time: currentTime,
        duration: totalDuration,
        episode_title: episode.title,
        podcast_title: episode.podcastTitle,
        podcast_url: episode.podcastUrl,
        image_url: episode.cover,
      }),
    }).then(() => loadHistory()).catch(() => {});
  }

  const loadBrowse = (genre = browseGenre) => {
    if (browseCache[genre]) {
      setBrowseResults(browseCache[genre]);
      return;
    }
    setBrowseLoading(true);
    apiFetch(`/api/podcasts/popular/?genre=${encodeURIComponent(genre)}`)
      .then(readJsonResponse)
      .then(data => {
        if (data.status !== 'ok') throw new Error(data.error || 'Не удалось загрузить каталог');
        setBrowseCache(cache => ({ ...cache, [genre]: data.items }));
        setBrowseResults(data.items);
      })
      .catch(e => console.warn(e.message))
      .finally(() => setBrowseLoading(false));
  };

  const logout = () => {
    localStorage.removeItem('jwt');
    setToken('');
    setUser(null);
    setPodcasts([]);
    setSelectedPodcast(null);
    setHistory([]);
    setProfileForm({ username: '', email: '', password: '' });
  };

  useEffect(() => {
    document.cookie = `theme=${theme}; path=/; max-age=31536000`;
  }, [theme]);

  useEffect(() => {
    loadPodcasts();
    if (token) {
      apiFetch('/api/podcasts/auth/me/')
        .then(readJsonResponse)
        .then(data => {
          setUser(data.user);
          setProfileForm({ username: data.user.username || '', email: data.user.email || '', password: '' });
        })
        .catch(() => logout());
    }
  }, [token]);

  useEffect(() => {
    loadHistory();
  }, [token]);

  useEffect(() => {
    if (activeTab === 'search' && browseResults.length === 0 && !browseLoading) loadBrowse();
  }, [activeTab]);

  useEffect(() => {
    if (!currentEpisode?.url || !audioRef.current) return;
    setUseDirectAudio(false);
    apiFetch(`/api/podcasts/progress/?episode_url=${encodeURIComponent(currentEpisode.url)}`)
      .then(readJsonResponse)
      .then(data => {
        const resumeAt = currentEpisode.resumeAt ?? data.current_time ?? 0;
        if (resumeAt > 0 && audioRef.current) {
          audioRef.current.currentTime = resumeAt;
          setPosition(resumeAt);
        }
        audioRef.current.volume = volume;
        return audioRef.current.play();
      })
      .then(() => setIsPlaying(true))
      .catch(e => console.warn(e.message));
  }, [currentEpisode]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  const categories = useMemo(() => ['all', ...Array.from(new Set(podcasts.map(p => p.category).filter(Boolean)))], [podcasts]);
  const visiblePodcasts = selectedCategory === 'all' ? podcasts : podcasts.filter(p => p.category === selectedCategory);

  const historyByUrl = useMemo(() => {
    const map = new Map();
    history.forEach(item => map.set(item.episode_url, item));
    return map;
  }, [history]);

  const currentIndex = podcastDetails?.entries?.findIndex(entry => getAudioUrl(entry) === currentEpisode?.url) ?? -1;
  const prevEpisodes = currentIndex > 0 ? podcastDetails.entries.slice(0, currentIndex) : [];
  const nextEpisodes = currentIndex >= 0 ? podcastDetails.entries.slice(currentIndex + 1, currentIndex + 4) : [];

  const updatePodcastFlag = (feedId, field, value) => {
    setPodcasts(items => items.map(item => item.id === feedId ? { ...item, [field]: value } : item));
    setSelectedPodcast(item => item?.id === feedId ? { ...item, [field]: value } : item);
  };

  const handleAddFeed = (prefilled = '', category = '') => {
    if (!token) {
      showNotice('Войдите в аккаунт, чтобы добавить подкаст в подписки.', 'Нужен вход');
      setActiveTab('profile');
      return Promise.resolve();
    }
    const metadata = typeof prefilled === 'object' && prefilled ? prefilled : { url: prefilled, category };
    if (!metadata.url) {
      setRssModalOpen(true);
      return Promise.resolve();
    }
    const url = metadata.url;
    if (!url) return Promise.resolve();
    setLoading(true);
    return apiFetch('/api/podcasts/add/', { method: 'POST', body: JSON.stringify({ ...metadata, url }) })
      .then(readJsonResponse)
      .then(data => {
        if (data.status !== 'ok') throw new Error(data.error || 'Не удалось добавить подкаст');
        loadPodcasts();
        if (selectedPodcast?.is_preview && selectedPodcast.url === url) {
          setSelectedPodcast({ ...data.item, is_preview: false, is_subscribed: true });
        }
        showNotice('Подкаст добавлен в обзор.', 'Подкаст добавлен');
      })
      .catch(e => showNotice(e.message, t('common.error')))
      .finally(() => setLoading(false));
  };

  const submitRssModal = (event) => {
    event.preventDefault();
    const url = rssUrl.trim();
    if (!url) return;
    setRssModalOpen(false);
    setRssUrl('');
    handleAddFeed(url);
  };

  const mergePodcastDetails = (previous, next) => {
    if (!previous) return next;
    const seen = new Set(previous.entries.map(entry => getAudioUrl(entry) || entry.title));
    const entries = [...previous.entries];
    next.entries.forEach(entry => {
      const key = getAudioUrl(entry) || entry.title;
      if (!seen.has(key)) entries.push(entry);
    });
    return { ...next, entries };
  };

  const loadPodcastPage = (podcast, offset = 0, append = false) => {
    if (append) setEpisodesLoadingMore(true);
    else setDetailsLoading(true);
    const endpoint = podcast.is_preview
      ? `/api/podcasts/preview/?offset=${offset}&limit=80`
      : `/api/podcasts/${podcast.id}/parse/?offset=${offset}&limit=80`;
    const options = podcast.is_preview ? { method: 'POST', body: JSON.stringify(podcast) } : {};
    return apiFetch(endpoint, options)
      .then(readJsonResponse)
      .then(data => {
        if (data.status === 'ok') {
          if (podcast.is_preview && data.item) setSelectedPodcast(data.item);
          setPodcastDetails(previous => append ? mergePodcastDetails(previous, data.data) : data.data);
        }
      })
      .catch(e => showNotice(e.message, t('common.error')))
      .finally(() => {
        setDetailsLoading(false);
        setEpisodesLoadingMore(false);
      });
  };

  const openPodcast = (podcast) => {
    setSelectedPodcast(podcast);
    setPodcastDetails(null);
    loadPodcastPage(podcast, 0, false);
  };

  const previewPodcast = (podcast) => {
    setSelectedPodcast({ ...podcast, is_preview: true });
    setPodcastDetails(null);
    loadPodcastPage({ ...podcast, is_preview: true }, 0, false);
  };

  function getAudioUrl(entry) {
    return entry?.audio_url || entry?.links?.find(l => l.rel === 'enclosure' || l.type?.startsWith('audio/'))?.href || '';
  }

  function getPlayableAudioUrl(url) {
    return url ? `/api/podcasts/audio/?url=${encodeURIComponent(url)}` : '';
  }

  function getEpisodeImage(entry) {
    return entry?.image_url || entry?.itunes_image?.href || entry?.image?.href || selectedPodcast?.image_url || podcastDetails?.feed?.image?.href || '';
  }

  const isCurrentEpisode = (entry) => getAudioUrl(entry) && getAudioUrl(entry) === currentEpisode?.url;

  const playEpisode = (entry) => {
    const audioLink = getAudioUrl(entry);
    if (!audioLink) {
      showNotice(t('common.noAudio'), t('common.error'));
      return;
    }
    if (audioLink === currentEpisode?.url) {
      togglePlay();
      return;
    }
    if (currentEpisode && audioRef.current) {
      saveProgress(currentEpisode, audioRef.current.currentTime || 0, audioRef.current.duration || duration || currentEpisode.duration || 0);
    }
    const progress = historyByUrl.get(audioLink);
    setUseDirectAudio(false);
    setDuration(entry.duration_seconds || 0);
    setPosition(progress?.current_time || 0);
    setCurrentEpisode({
      url: audioLink,
      title: entry.title,
      podcastTitle: podcastDetails?.feed?.title || selectedPodcast.title,
      podcastUrl: selectedPodcast?.url || '',
      cover: getEpisodeImage(entry),
      duration: entry.duration_seconds || 0,
      resumeAt: progress?.current_time || 0,
    });
  };

  const playHistory = (item) => {
    setUseDirectAudio(false);
    setDuration(item.duration || 0);
    setPosition(item.current_time || 0);
    setCurrentEpisode({
      url: item.episode_url,
      title: item.episode_title,
      podcastTitle: item.podcast_title,
      podcastUrl: item.podcast_url,
      cover: item.image_url,
      duration: item.duration || 0,
      resumeAt: item.current_time || 0,
    });
  };

  const submitAuth = (event) => {
    event.preventDefault();
    apiFetch(`/api/podcasts/auth/${authMode === 'register' ? 'register' : 'login'}/`, {
      method: 'POST',
      body: JSON.stringify(authForm),
    })
      .then(readJsonResponse)
      .then(data => {
        if (data.status !== 'ok') throw new Error(data.error || 'Не удалось войти');
        localStorage.setItem('jwt', data.token);
        setToken(data.token);
        setUser(data.user);
        setProfileForm({ username: data.user.username || '', email: data.user.email || '', password: '' });
        setActiveTab('overview');
      })
      .catch(e => showNotice(e.message, t('common.error')));
  };

  const submitProfile = (event) => {
    event.preventDefault();
    apiFetch('/api/podcasts/auth/profile/', { method: 'POST', body: JSON.stringify(profileForm) })
      .then(readJsonResponse)
      .then(data => {
        if (data.status !== 'ok') throw new Error(data.error || 'Не удалось сохранить профиль');
        localStorage.setItem('jwt', data.token);
        setToken(data.token);
        setUser(data.user);
        setProfileForm({ username: data.user.username || '', email: data.user.email || '', password: '' });
        showNotice('Профиль сохранен.');
      })
      .catch(e => showNotice(e.message, t('common.error')));
  };

  const toggleSubscription = (feed) => {
    if (!token) {
      showNotice('Войдите в аккаунт, чтобы управлять подписками.', 'Нужен вход');
      setActiveTab('profile');
      return;
    }
    if (feed.is_preview) {
      handleAddFeed(feed);
      return;
    }
    apiFetch('/api/podcasts/subscriptions/toggle/', { method: 'POST', body: JSON.stringify({ feed_id: feed.id }) })
      .then(readJsonResponse)
      .then(data => {
        if (data.status === 'ok') {
          updatePodcastFlag(feed.id, 'is_subscribed', data.active);
          loadPodcasts();
          showNotice(data.active ? 'Подкаст добавлен в обзор.' : 'Подкаст убран из обзора.', data.active ? 'Подписка включена' : 'Подписка отключена');
        }
      });
  };

  const searchOpenDirectory = (event) => {
    event.preventDefault();
    if (searchQuery.trim().length < 2) return;
    setSearchLoading(true);
    apiFetch(`/api/podcasts/search/?q=${encodeURIComponent(searchQuery.trim())}`)
      .then(readJsonResponse)
      .then(data => {
        if (data.status === 'ok') setSearchResults(data.items);
      })
      .catch(e => showNotice(e.message, t('common.error')))
      .finally(() => setSearchLoading(false));
  };

  const changeBrowseGenre = (genre) => {
    setBrowseGenre(genre);
    setSearchResults([]);
    setSearchQuery('');
    loadBrowse(genre);
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (audioRef.current.paused) audioRef.current.play().then(() => setIsPlaying(true));
    else {
      audioRef.current.pause();
      setIsPlaying(false);
      saveProgress();
    }
  };

  const seekTo = (event) => {
    if (!audioRef.current) return;
    const next = Number(event.target.value);
    audioRef.current.currentTime = next;
    setPosition(next);
  };

  const skipToNext = () => {
    if (shuffleEnabled && podcastDetails?.entries?.length) {
      const playable = podcastDetails.entries.filter(entry => getAudioUrl(entry) && getAudioUrl(entry) !== currentEpisode?.url);
      if (playable.length) playEpisode(playable[(Math.max(currentIndex, 0) + 7) % playable.length]);
      return;
    }
    if (nextEpisodes.length > 0) playEpisode(nextEpisodes[0]);
  };

  const skipToPrevious = () => {
    if (audioRef.current && audioRef.current.currentTime > 5) {
      audioRef.current.currentTime = 0;
      setPosition(0);
      return;
    }
    if (prevEpisodes.length > 0) playEpisode(prevEpisodes[prevEpisodes.length - 1]);
  };

  const formatTime = (seconds) => {
    if (!Number.isFinite(seconds) || seconds <= 0) return '0:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    return hrs > 0 ? `${hrs}:${String(mins).padStart(2, '0')}:${secs}` : `${mins}:${secs}`;
  };

  const formatEpisodeDuration = (entry) => {
    const seconds = entry?.duration_seconds || 0;
    if (seconds > 0) {
      const minutes = Math.round(seconds / 60);
      if (minutes >= 60) return `${Math.floor(minutes / 60)} ч. ${minutes % 60} мин.`;
      return `${minutes} мин.`;
    }
    return '';
  };

  const progressPercent = (item) => item?.duration ? Math.min(100, Math.round((item.current_time / item.duration) * 100)) : 0;
  const directoryItems = searchQuery.trim().length >= 2 || searchResults.length ? searchResults : browseResults;
  const directoryLoading = searchLoading || browseLoading;

  const PodcastCard = ({ podcast, index = 0 }) => (
    <div className={`podcast-card ${classes[index % classes.length]}`} onClick={() => openPodcast(podcast)} style={{ cursor: 'pointer' }}>
      <div className="card-bg" style={podcast.image_url ? { backgroundImage: `url(${podcast.image_url})` } : undefined}></div>
      <div className="card-content">
        <div className="card-actions" onClick={event => event.stopPropagation()}>
          <button className={`mini-action ${podcast.is_subscribed ? 'active' : ''}`} title="Подписаться" onClick={() => toggleSubscription(podcast)}><IconCheck /></button>
        </div>
        <div className="card-bottom">
          <div className="card-text">
            <div className="card-title">{podcast.title || 'Без названия'}</div>
            <div className="card-author">{podcast.category || 'Без категории'}</div>
          </div>
          <div className="play-btn"><IconPlay /></div>
        </div>
      </div>
    </div>
  );

  const renderCards = (items) => (
    <div className="cards-grid">
      {items.length === 0 && <div className="empty-state">{t('common.noPodcasts')}</div>}
      {items.map((p, i) => <PodcastCard podcast={p} index={i} key={p.id || p.url} />)}
    </div>
  );

  const renderHistoryStrip = () => {
    const active = history.filter(item => !item.completed).slice(0, 4);
    if (!active.length) return null;
    return (
      <section className="continue-strip">
        <h3>Продолжить слушать</h3>
        <div className="continue-grid">
          {active.map(item => (
            <button className="continue-item" key={item.episode_url} onClick={() => playHistory(item)}>
              {item.image_url && <img src={item.image_url} alt="" />}
              <span>{item.episode_title}</span>
              <small>{formatTime(item.current_time)} • {progressPercent(item)}%</small>
            </button>
          ))}
        </div>
      </section>
    );
  };

  const renderAuth = () => (
    <div className="panel-card auth-panel">
      <h2>{authMode === 'register' ? 'Регистрация' : 'Вход'}</h2>
      <p>Войдите, чтобы синхронизировать подписки и прогресс прослушивания.</p>
      <form onSubmit={submitAuth} className="stack-form">
        <input value={authForm.username} onChange={e => setAuthForm({ ...authForm, username: e.target.value })} placeholder="Логин" autoComplete="username" />
        {authMode === 'register' && <input value={authForm.email} onChange={e => setAuthForm({ ...authForm, email: e.target.value })} placeholder="Email" autoComplete="email" />}
        <input type="password" value={authForm.password} onChange={e => setAuthForm({ ...authForm, password: e.target.value })} placeholder="Пароль" autoComplete={authMode === 'register' ? 'new-password' : 'current-password'} />
        <button className="primary-btn" type="submit">{authMode === 'register' ? 'Создать аккаунт' : 'Войти'}</button>
      </form>
      <button className="link-btn" onClick={() => setAuthMode(authMode === 'register' ? 'login' : 'register')}>
        {authMode === 'register' ? 'Уже есть аккаунт' : 'Нужен аккаунт'}
      </button>
    </div>
  );

  const renderSearch = () => (
    <div className="search-view">
      <form className="search-bar discovery-search" onSubmit={searchOpenDirectory}>
        <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Искать подкасты по названию, автору или теме" />
        <button className="primary-btn" type="submit"><IconSearch /> Найти</button>
      </form>
      <div className="browse-toolbar">
        {browseGenres.map(([key, label]) => (
          <button className={`cat-pill ${browseGenre === key && searchResults.length === 0 ? 'active' : ''}`} key={key} onClick={() => changeBrowseGenre(key)}>
            {label}
          </button>
        ))}
      </div>
      {directoryLoading ? <div className="empty-state">Загружаем подборку...</div> : (
        <div className="search-results">
          {directoryItems.map(result => (
            <div className="search-result" key={result.url} onClick={() => previewPodcast(result)}>
              {result.image_url ? <img src={result.image_url} alt="" /> : <div className="search-cover-fallback"><IconRSS /></div>}
              <div>
                <div className="search-title">{result.title}</div>
                <div className="search-meta">{[result.author, result.category].filter(Boolean).join(' • ')}</div>
              </div>
              <button className="primary-btn" onClick={(event) => { event.stopPropagation(); handleAddFeed(result); }}>Добавить</button>
            </div>
          ))}
          {directoryItems.length === 0 && <div className="empty-state">Ничего не нашли. Попробуйте другую тему или запрос.</div>}
        </div>
      )}
    </div>
  );

  const renderProfile = () => {
    if (!user) return renderAuth();
    return (
      <div className="profile-grid">
        <div className="panel-card profile-card">
          <h2>{user.username}</h2>
          <p>Синхронизация включена. Можно менять публичное имя, email и пароль.</p>
          <form onSubmit={submitProfile} className="stack-form">
            <input value={profileForm.username} onChange={e => setProfileForm({ ...profileForm, username: e.target.value })} placeholder="Логин" autoComplete="username" />
            <input value={profileForm.email} onChange={e => setProfileForm({ ...profileForm, email: e.target.value })} placeholder="Email" autoComplete="email" />
            <input type="password" value={profileForm.password} onChange={e => setProfileForm({ ...profileForm, password: e.target.value })} placeholder="Новый пароль, если нужно" autoComplete="new-password" />
            <button className="primary-btn" type="submit">Сохранить профиль</button>
          </form>
        </div>
        <div className="panel-card profile-card">
          <h2>Активность</h2>
          <div className="profile-stats">
            <span><b>{podcasts.length}</b> подписок</span>
            <span><b>{history.filter(item => item.completed).length}</b> прослушано</span>
          </div>
          <button className="link-btn danger-link" onClick={logout}>Выйти</button>
        </div>
      </div>
    );
  };

  const renderEpisode = (ep, idx) => {
    const audioUrl = getAudioUrl(ep);
    const progress = historyByUrl.get(audioUrl);
    const playing = isCurrentEpisode(ep) && isPlaying;
    const image = getEpisodeImage(ep);
    return (
      <div className={`ep-item ${progress?.completed ? 'completed' : ''}`} key={`${ep.title}-${idx}`} onClick={() => playEpisode(ep)}>
        <div className="ep-cover-wrapper">
          {image ? <img src={image} alt="" className="ep-cover" /> : <div className="ep-cover-fallback"><IconRSS /></div>}
          <div className="ep-cover-overlay always">{playing ? <IconPause /> : <IconPlay />}</div>
        </div>
        <div className="ep-details">
          <div className="ep-title">{ep.title}</div>
          <div className="ep-meta">
            <span className="ep-date">{formatDate(ep.published)}</span>
            {formatEpisodeDuration(ep) && <span className="ep-duration">{formatEpisodeDuration(ep)}</span>}
            {progress && !progress.completed && <span>{progressPercent(progress)}% прослушано</span>}
            {progress?.completed && <span className="done-label">Прослушано</span>}
          </div>
        </div>
      </div>
    );
  };

  const detailTitle = selectedPodcast?.is_preview ? 'Предпросмотр' : 'Подкаст';

  return (
    <div className={`app-container ${theme}`}>
      <aside className="sidebar">
        <div className="logo" onClick={() => { setSelectedPodcast(null); setActiveTab('overview'); }}>
          <div className="logo-icon">E</div>
          Easy Podcasts
        </div>
        <ul className="nav-menu">
          <li className={`nav-item ${activeTab === 'overview' && !selectedPodcast ? 'active' : ''}`} onClick={() => { setActiveTab('overview'); setSelectedPodcast(null); }}><IconHome /> {t('nav.overview')}</li>
          <li className={`nav-item ${activeTab === 'search' ? 'active' : ''}`} onClick={() => { setActiveTab('search'); setSelectedPodcast(null); }}><IconSearch /> Каталог</li>
        </ul>
        <div className="nav-divider"></div>
        <ul className="nav-menu">
          <li className="nav-item" onClick={() => handleAddFeed()}><IconRSS /> {t('nav.addViaRss')}</li>
          <li className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => { setActiveTab('profile'); setSelectedPodcast(null); }}><IconUser /> {user ? user.username : t('nav.profile')}</li>
        </ul>
      </aside>

      <main className="main-content" style={{ paddingBottom: currentEpisode ? '120px' : '3rem' }}>
        <header className="header">
          <div>
            <div className="header-title">
              {selectedPodcast ? detailTitle : activeTab === 'search' ? 'Каталог' : activeTab === 'profile' ? 'Профиль' : t('nav.overview')}
            </div>
            {!selectedPodcast && <p className="header-subtitle">Слушайте, сохраняйте и открывайте новые подкасты.</p>}
          </div>
          <div className="user-profile">
            <button className="theme-toggle" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} title="Сменить тему">
              {theme === 'light' ? <IconMoon /> : <IconSun />}
            </button>
            <div className="user-info">
              <span className="user-name">{user?.username || t('player.guest')}</span>
            </div>
            {user && <button className="link-btn" onClick={logout}>Выйти</button>}
            <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.username || t('player.guest'))}&background=ef1e5d&color=fff`} alt="" className="user-avatar" />
          </div>
        </header>

        {selectedPodcast ? (
          <div className="podcast-detail-view">
            {detailsLoading ? (
              <div className="podcast-detail-skeleton-full">
                <div className="skeleton-back-btn-lg"></div>
                <div className="podcast-detail-header"><div className="skeleton-cover-lg"></div><div className="skeleton-info"><div className="skeleton-title-lg"></div><div className="skeleton-desc-sm"></div></div></div>
                <div className="skeleton-episodes-full"><h3 className="skeleton-h3-text">{t('common.episodes')}</h3><SkeletonEpisode /><SkeletonEpisode /><SkeletonEpisode /></div>
              </div>
            ) : (
              <>
                <button className="back-btn-lg" onClick={() => setSelectedPodcast(null)} title="Назад"><IconBack /></button>
                <div className="podcast-detail-header">
                  {selectedPodcast.image_url && <img src={selectedPodcast.image_url} alt="" className="pd-cover" />}
                  <div className="pd-info">
                    <div className="pd-kicker">{selectedPodcast.category || podcastDetails?.feed?.author || 'Podcast'}</div>
                    <div className="pd-title-lg">{selectedPodcast.title}</div>
                    <div className="pd-actions">
                      {selectedPodcast.is_preview ? (
                        <button className="chip-btn active" onClick={() => handleAddFeed(selectedPodcast)}>Добавить в библиотеку</button>
                      ) : (
                        <>
                          <button className={`chip-btn ${selectedPodcast.is_subscribed ? 'active' : ''}`} onClick={() => toggleSubscription(selectedPodcast)}>{selectedPodcast.is_subscribed ? 'В подписках' : 'Подписаться'}</button>
                        </>
                      )}
                    </div>
                    <div className="pd-desc-card" dangerouslySetInnerHTML={{ __html: selectedPodcast.description || podcastDetails?.feed?.description || podcastDetails?.feed?.summary || 'Описание недоступно' }}></div>
                  </div>
                </div>
                <div className="episodes-list">
                  <div className="episodes-heading">
                    <h3>{t('common.episodes')}</h3>
                    {podcastDetails?.entry_count > podcastDetails?.entries?.length && <span>Показаны {podcastDetails.entries.length} из {podcastDetails.entry_count}</span>}
                  </div>
                  {podcastDetails?.entries?.map(renderEpisode)}
                  {podcastDetails?.has_more && (
                    <button className="load-more-episodes" disabled={episodesLoadingMore} onClick={() => loadPodcastPage(selectedPodcast, podcastDetails.next_offset, true)}>
                      {episodesLoadingMore ? 'Загружаем...' : `Показать ещё ${Math.min(80, podcastDetails.entry_count - podcastDetails.entries.length)} эпизодов`}
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        ) : activeTab === 'overview' ? (
          <>
            {renderHistoryStrip()}
            <div className="categories">
              {categories.map(category => (
                <button className={`cat-item ${selectedCategory === category ? 'active' : ''}`} key={category} onClick={() => setSelectedCategory(category)}>
                  {category === 'all' ? 'Все' : category}
                </button>
              ))}
            </div>
            {loading ? <div className="cards-grid"><SkeletonCard /><SkeletonCard /><SkeletonCard /><SkeletonCard /></div> : renderCards(visiblePodcasts)}
          </>
        ) : activeTab === 'search' ? renderSearch() : renderProfile()}
      </main>

      {currentEpisode && (
        <div className="audio-player-bar custom-player">
          <div className="np-info">
            {currentEpisode.cover && <img src={currentEpisode.cover} className="np-img" alt="" />}
            <div className="np-text">
              <div className="np-title" title={currentEpisode.title}>{currentEpisode.title}</div>
              {currentEpisode.podcastTitle && currentEpisode.podcastTitle !== currentEpisode.title && <div className="np-podcast">{currentEpisode.podcastTitle}</div>}
            </div>
          </div>
          <div className="np-controls">
            <div className="player-buttons">
              <button className={shuffleEnabled ? 'active' : ''} onClick={() => setShuffleEnabled(value => !value)} title="Перемешать"><IconShuffle /></button>
              <button onClick={skipToPrevious} disabled={!prevEpisodes.length && position <= 5} title="Предыдущий эпизод"><IconPrev /></button>
              <button className="player-main-btn" onClick={togglePlay} title={isPlaying ? 'Пауза' : 'Играть'}>{isPlaying ? <IconPause /> : <IconPlay />}</button>
              <button onClick={skipToNext} disabled={!shuffleEnabled && !nextEpisodes.length} title="Следующий эпизод"><IconNext /></button>
              <button className={repeatEnabled ? 'active' : ''} onClick={() => setRepeatEnabled(value => !value)} title="Повтор"><IconRepeat /></button>
            </div>
            <div className="progress-row">
              <span>{formatTime(position)}</span>
              <input type="range" min="0" max={duration || currentEpisode.duration || 0} step="1" value={Math.min(position, duration || currentEpisode.duration || 0)} onChange={seekTo} />
              <span>{formatTime(duration || currentEpisode.duration)}</span>
            </div>
            <audio
              ref={audioRef}
              src={useDirectAudio ? currentEpisode.url : getPlayableAudioUrl(currentEpisode.url)}
              autoPlay
              onLoadedMetadata={() => setDuration(audioRef.current?.duration || currentEpisode.duration || 0)}
              onTimeUpdate={() => setPosition(audioRef.current?.currentTime || 0)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => {
                setIsPlaying(false);
                if (audioRef.current?.ended) return;
                saveProgress();
              }}
              onEnded={() => {
                setIsPlaying(false);
                saveProgress();
                if (repeatEnabled && audioRef.current) {
                  audioRef.current.currentTime = 0;
                  audioRef.current.play();
                } else {
                  skipToNext();
                }
              }}
              onError={() => {
                if (!useDirectAudio && currentEpisode?.url) {
                  setUseDirectAudio(true);
                  showNotice('Серверный поток не ответил. Пробую прямое подключение к источнику.', 'Переключаю источник');
                } else {
                  showNotice('Источник аудио не отдал файл. Попробуйте другой эпизод или повторите позже.', t('common.error'));
                }
              }}
            />
          </div>
          <div className="player-volume">
            <IconVolume />
            <input type="range" min="0" max="1" step="0.05" value={volume} onChange={e => setVolume(Number(e.target.value))} />
          </div>
          <button className="close-player" onClick={() => { saveProgress(); setCurrentEpisode(null); setIsPlaying(false); }} title="Закрыть" aria-label="Закрыть плеер"><IconClose /></button>
        </div>
      )}

      {notice && (
        <div className="notice-backdrop" onClick={() => setNotice(null)}>
          <div className="notice-card" onClick={event => event.stopPropagation()} role="status" aria-live="polite">
            <h2>{notice.title}</h2>
            <p>{notice.message}</p>
            <button className="primary-btn" type="button" onClick={() => setNotice(null)}>OK</button>
          </div>
        </div>
      )}

      {rssModalOpen && (
        <div className="modal-backdrop" onClick={() => setRssModalOpen(false)}>
          <form className="rss-modal" onSubmit={submitRssModal} onClick={event => event.stopPropagation()}>
            <h2>Добавить RSS</h2>
            <p>Вставьте ссылку на RSS-ленту подкаста.</p>
            <input value={rssUrl} onChange={event => setRssUrl(event.target.value)} placeholder="https://example.com/feed.xml" autoFocus />
            <div className="modal-actions">
              <button className="link-btn" type="button" onClick={() => setRssModalOpen(false)}>Отмена</button>
              <button className="primary-btn" type="submit">Добавить</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <I18nProvider initialLocale="ru">
      <AppContent />
    </I18nProvider>
  );
}

export default App;
