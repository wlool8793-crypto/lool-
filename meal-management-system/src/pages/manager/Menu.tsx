import React, { useState, useEffect } from 'react';
import {
  Plus,
  Calendar,
  Coffee,
  UtensilsCrossed,
  Moon,
  Edit,
  Trash2,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  Save,
  X,
} from 'lucide-react';
import { Button } from '../../components/forms/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import {
  getMenuByDate,
  getUpcomingMenus,
  upsertMenu,
  deleteMenu,
} from '../../services/menu.service';
import { Menu as MenuType, InsertMenu } from '../../types/database.types';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

export const Menu: React.FC = () => {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [currentMenu, setCurrentMenu] = useState<MenuType | null>(null);
  const [upcomingMenus, setUpcomingMenus] = useState<MenuType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Form state
  const [formData, setFormData] = useState<InsertMenu>({
    menu_date: new Date().toISOString().split('T')[0],
    breakfast_items: '',
    lunch_items: '',
    dinner_items: '',
    created_by: user?.id || '',
  });

  const fetchMenuForDate = async (date: string) => {
    try {
      const result = await getMenuByDate(date);

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch menu');
      }

      setCurrentMenu(result.data);

      if (result.data) {
        setFormData({
          menu_date: result.data.menu_date,
          breakfast_items: result.data.breakfast_items || '',
          lunch_items: result.data.lunch_items || '',
          dinner_items: result.data.dinner_items || '',
          created_by: user?.id || result.data.created_by || '',
        });
        setEditMode(false);
      } else {
        // No menu for this date, prepare for creation
        setFormData({
          menu_date: date,
          breakfast_items: '',
          lunch_items: '',
          dinner_items: '',
          created_by: user?.id || '',
        });
        setEditMode(true);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch menu');
    }
  };

  const fetchUpcomingMenus = async () => {
    try {
      const result = await getUpcomingMenus(7);

      if (!result.success) {
        throw new Error(result.error || 'Failed to fetch upcoming menus');
      }

      setUpcomingMenus(result.data || []);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to fetch upcoming menus');
    }
  };

  const handleSaveMenu = async () => {
    if (!formData.breakfast_items && !formData.lunch_items && !formData.dinner_items) {
      toast.error('Please add at least one meal item');
      return;
    }

    setSaving(true);
    try {
      const result = await upsertMenu(formData);

      if (!result.success) {
        throw new Error(result.error || 'Failed to save menu');
      }

      toast.success('Menu saved successfully');
      await fetchMenuForDate(selectedDate);
      await fetchUpcomingMenus();
      setEditMode(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to save menu');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteMenu = async () => {
    if (!currentMenu) return;

    if (!confirm('Are you sure you want to delete this menu?')) {
      return;
    }

    setSaving(true);
    try {
      const result = await deleteMenu(currentMenu.id);

      if (!result.success) {
        throw new Error(result.error || 'Failed to delete menu');
      }

      toast.success('Menu deleted successfully');
      await fetchMenuForDate(selectedDate);
      await fetchUpcomingMenus();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to delete menu');
    } finally {
      setSaving(false);
    }
  };

  const handleDateChange = (days: number) => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + days);
    const newDate = date.toISOString().split('T')[0];
    setSelectedDate(newDate);
  };

  const handleCancelEdit = () => {
    if (currentMenu) {
      setFormData({
        menu_date: currentMenu.menu_date,
        breakfast_items: currentMenu.breakfast_items || '',
        lunch_items: currentMenu.lunch_items || '',
        dinner_items: currentMenu.dinner_items || '',
        created_by: user?.id || currentMenu.created_by || '',
      });
      setEditMode(false);
    } else {
      setFormData({
        menu_date: selectedDate,
        breakfast_items: '',
        lunch_items: '',
        dinner_items: '',
        created_by: user?.id || '',
      });
    }
  };

  useEffect(() => {
    if (user) {
      setFormData((prev) => ({ ...prev, created_by: user.id }));
    }
  }, [user]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchMenuForDate(selectedDate), fetchUpcomingMenus()]);
      setLoading(false);
    };

    loadData();
  }, [selectedDate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Menu Management</h1>
          <p className="text-gray-600 mt-1">Plan and manage daily meal menus</p>
        </div>
      </div>

      {/* Date Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Select Date</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleDateChange(-1)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleDateChange(1)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
              className="ml-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              Today
            </button>
          </div>
        </div>

        <div className="text-center py-2">
          <p className="text-2xl font-bold text-gray-900">
            {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
      </div>

      {/* Menu Editor */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Menu for {new Date(selectedDate + 'T00:00:00').toLocaleDateString()}
          </h3>
          <div className="flex gap-2">
            {!editMode && currentMenu && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditMode(true)}
                  leftIcon={<Edit className="w-4 h-4" />}
                >
                  Edit
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleDeleteMenu}
                  disabled={saving}
                  leftIcon={<Trash2 className="w-4 h-4" />}
                >
                  Delete
                </Button>
              </>
            )}
            {editMode && (
              <>
                <Button variant="outline" size="sm" onClick={handleCancelEdit} leftIcon={<X className="w-4 h-4" />}>
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSaveMenu}
                  disabled={saving}
                  leftIcon={<Save className="w-4 h-4" />}
                >
                  {saving ? 'Saving...' : 'Save Menu'}
                </Button>
              </>
            )}
            {!editMode && !currentMenu && (
              <Button size="sm" onClick={() => setEditMode(true)} leftIcon={<Plus className="w-4 h-4" />}>
                Add Menu
              </Button>
            )}
          </div>
        </div>

        <div className="space-y-6">
          {/* Breakfast */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-yellow-50 rounded-lg p-2">
                <Coffee className="w-5 h-5 text-yellow-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Breakfast</h4>
            </div>
            {editMode ? (
              <textarea
                value={formData.breakfast_items}
                onChange={(e) => setFormData({ ...formData, breakfast_items: e.target.value })}
                placeholder="Enter breakfast items (e.g., Idli, Sambar, Chutney)"
                rows={3}
                className="block w-full px-4 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <p className="text-gray-700 whitespace-pre-wrap">
                {formData.breakfast_items || 'No items added'}
              </p>
            )}
          </div>

          {/* Lunch */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-orange-50 rounded-lg p-2">
                <UtensilsCrossed className="w-5 h-5 text-orange-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Lunch</h4>
            </div>
            {editMode ? (
              <textarea
                value={formData.lunch_items}
                onChange={(e) => setFormData({ ...formData, lunch_items: e.target.value })}
                placeholder="Enter lunch items (e.g., Rice, Dal, Sabzi, Roti)"
                rows={3}
                className="block w-full px-4 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <p className="text-gray-700 whitespace-pre-wrap">
                {formData.lunch_items || 'No items added'}
              </p>
            )}
          </div>

          {/* Dinner */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-indigo-50 rounded-lg p-2">
                <Moon className="w-5 h-5 text-indigo-600" />
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Dinner</h4>
            </div>
            {editMode ? (
              <textarea
                value={formData.dinner_items}
                onChange={(e) => setFormData({ ...formData, dinner_items: e.target.value })}
                placeholder="Enter dinner items (e.g., Chapati, Paneer, Dal, Rice)"
                rows={3}
                className="block w-full px-4 py-2.5 text-gray-900 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            ) : (
              <p className="text-gray-700 whitespace-pre-wrap">
                {formData.dinner_items || 'No items added'}
              </p>
            )}
          </div>
        </div>

        {!currentMenu && !editMode && (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 mb-4">No menu set for this date</p>
            <Button onClick={() => setEditMode(true)} leftIcon={<Plus className="w-4 h-4" />}>
              Add Menu
            </Button>
          </div>
        )}
      </div>

      {/* Upcoming Menus */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Menus (Next 7 Days)</h3>

        {upcomingMenus.length > 0 ? (
          <div className="space-y-4">
            {upcomingMenus.map((menu) => (
              <div
                key={menu.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => setSelectedDate(menu.menu_date)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-semibold text-gray-900">
                        {new Date(menu.menu_date + 'T00:00:00').toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                      <p className="text-sm text-gray-500">
                        {menu.menu_date === new Date().toISOString().split('T')[0]
                          ? 'Today'
                          : menu.menu_date ===
                            new Date(Date.now() + 86400000).toISOString().split('T')[0]
                          ? 'Tomorrow'
                          : ''}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-700 mb-1">Breakfast</p>
                    <p className="text-gray-600 line-clamp-2">
                      {menu.breakfast_items || 'Not set'}
                    </p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700 mb-1">Lunch</p>
                    <p className="text-gray-600 line-clamp-2">{menu.lunch_items || 'Not set'}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700 mb-1">Dinner</p>
                    <p className="text-gray-600 line-clamp-2">{menu.dinner_items || 'Not set'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Calendar}
            title="No Upcoming Menus"
            description="No menus have been set for the upcoming week"
          />
        )}
      </div>
    </div>
  );
};

export default Menu;
