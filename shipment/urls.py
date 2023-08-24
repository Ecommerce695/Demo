from django.urls import path
from .views import (CreateShipmentForOrder, GetOrderDetails,PickupRequest, GenerateAWB,GetPickupLocations, ChangePickupLocation,
                    ChangeDeliveryLocation,CancelOrder,GetallOrders, ListReturnOrders,
                    AllShipmentDetails,SingleShipmentDetails,ExportAddress,CouriersList,DomesticCourierServiceability)

from .forward_shipping import (CreateShipmentForEachOrder,GenerateAWB_Pickup,ShipmentTracking,OrderStatusView,GenerateManifest,
                    GenerateLabel,GenerateInvoice,RefreshOrderStatusView,CancelShipment,)
from .return_shipping import (CreateReturnAPI,GenerateReturnAWB,)

urlpatterns = [
    
# Forward Shipment APIs
    #Create Order in Shiprocket through API
    path("create-orders/<token>/<int:oid>", CreateShipmentForEachOrder.as_view(),name="Create Order in Shipment"),
    #Generate AWB and Assigning Courier Partner API
    path('generate_pickup/<token>/<shipmentid>',GenerateAWB_Pickup.as_view(),name='Generate Pickup and AWB'),
    #Track Order API
    path("track/<token>/<int:shipmentid>",ShipmentTracking.as_view(),name='Track Order'),
    #Get Order Details along with shipping status API
    path("order_status/<token>/<int:oid>",OrderStatusView.as_view(),name='Check Status of Order'),
    # Labels | Invoice | ManiFest APIs
    path("generate/manifest/<token>/<int:shipmentid>",GenerateManifest.as_view(),name='Generate Manifest'),
    # path("print/manifest/<token>/<int:shipmentid>",PrintManifest.as_view(),name='Print Generated manifest'),
    path("generate/label/<token>/<int:shipmentid>",GenerateLabel.as_view(),name='Generate Label'),
    path("generate/invoice/<token>/<int:shipmentid>",GenerateInvoice.as_view(),name='Generate Invoice'),
    # This API will refresh all Orders Shipment Status 
    path('refresh/order_status/<token>', RefreshOrderStatusView.as_view(),name='Refresh All Order Status'),
    # This will Cancel the Shipment assigned to Order
    path("cancel-shipment/<token>/<shipmentid>", CancelShipment.as_view(),name="Cancel Shipment"),


# Return Shipment APIs
    # Create Return Order 
    path("create-return/<token>/<oid>", CreateReturnAPI.as_view(),name="Create Return Order"),
    # Generate AWB and assign Courier for Return Product
    path("generte-return-awb/<token>/<oid>", GenerateReturnAWB.as_view(),name="Generate Return AWB"),

    

    # Create/Update Module
    path("create-order/<token>/<int:oid>", CreateShipmentForOrder.as_view(),name="Shipment "),
    path("pickup-locations/", GetPickupLocations.as_view(),name="Get all Pickup location Details"),
    path("change-pickup-location/<oid>/<pl>", ChangePickupLocation.as_view(),name="Change Pickup Location"),
    path("change-delivery-location/<token>/<oid>/<aid>", ChangeDeliveryLocation.as_view(),name="Change Delivery Location"),
    path("cancel-order/<token>/<oid>", CancelOrder.as_view(),name="Cancel Order"),

    # Courier Module
    path("generate-pickup/<token>/<int:sid>", PickupRequest.as_view(),name="Pickup Request"),
    path("generate-awb/<token>/<int:sid>", GenerateAWB.as_view(),name="Generate AWB"),
    path('list-couriers/',CouriersList.as_view(),name='courier list'),
    path('check-domestic-service',DomesticCourierServiceability.as_view(),name=''),

    # Orders Module
    path("all-orders-details/", GetallOrders.as_view(),name="List all Orders"),
    path("order-status/<token>/<int:oid>", GetOrderDetails.as_view(),name="Order Details"),
    
    # path("list-return-orders/", ListReturnOrders.as_view(),name="List all Return Order"),
    
    #Shipment Module
    path("all-shipment-details/", AllShipmentDetails.as_view(),name="All Shipment Details"),
    path("single-shipment-details/<sid>", SingleShipmentDetails.as_view(),name="Single Shipment Details"),
    

    # This API will Export All Addresses Present for Org to Shiprocket Pickup Location Addresses
    path('exportalladdresses', ExportAddress.as_view(),name='Dump all Org Company addresses to Shipment'),

]   