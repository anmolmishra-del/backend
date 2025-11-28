
from sqladmin import ModelView

from app.modules.food_delivery.model import MenuCategory, MenuItem, Restaurant, RestaurantLocation


class RestaurantAdmin(ModelView, model=Restaurant):
    name = "Restaurant"
    name_plural = "Restaurants"
    column_list = [Restaurant.id, Restaurant.name,  Restaurant.cuisine_type, Restaurant.phone_number, Restaurant.email, Restaurant.status]
    form_columns = [Restaurant.name, Restaurant.cuisine_type, Restaurant.phone_number, Restaurant.email, Restaurant.logo_url, Restaurant.banner_url, Restaurant.status, Restaurant.is_favorite]    
class RestaurantLocatinAdmin(ModelView, model=RestaurantLocation):
    name = "Restaurant Location"
    name_plural = "Restaurants Locations"
    column_list = [RestaurantLocation.id, RestaurantLocation.restaurant_id, RestaurantLocation.address, RestaurantLocation.city, RestaurantLocation.state, RestaurantLocation.country]
    form_columns = [RestaurantLocation.restaurant_id, RestaurantLocation.latitude, RestaurantLocation.longitude, RestaurantLocation.address, RestaurantLocation.city, RestaurantLocation.state, RestaurantLocation.country, RestaurantLocation.postal_code, RestaurantLocation.location_id, RestaurantLocation.dining_type]
class MenuCategoryAdmin(ModelView, model=MenuCategory):
    name = "Menu Category"
    name_plural = "Menu Categories"
    column_list = [MenuCategory.id,  MenuCategory.name]
    form_columns = [ MenuCategory.name]

  


class MenuItemAdmin(ModelView, model=MenuItem):
    name = "Menu Item"
    name_plural = "Menu Items"
    column_list = [MenuItem.id, MenuItem.category_id, MenuItem.name, MenuItem.price, MenuItem.is_available]
    form_columns = [MenuItem.category_id, MenuItem.name, MenuItem.description, MenuItem.price, MenuItem.is_available, MenuItem.image_url]   