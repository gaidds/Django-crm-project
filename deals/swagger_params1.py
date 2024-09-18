from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

organization_params_in_header = organization_params_in_header = OpenApiParameter(
    "org", OpenApiTypes.STR, OpenApiParameter.HEADER
)

organization_params = [
    organization_params_in_header,
]

deal_list_get_params = [
    organization_params_in_header,
    OpenApiParameter("deal_name", OpenApiTypes.STR, OpenApiParameter.QUERY),
    OpenApiParameter("source", OpenApiTypes.STR, OpenApiParameter.QUERY),
    OpenApiParameter("assigned_to", OpenApiTypes.STR, OpenApiParameter.QUERY),
    OpenApiParameter("account", OpenApiTypes.STR,OpenApiParameter.QUERY),
    OpenApiParameter(
        "stage",
        OpenApiTypes.STR,
        OpenApiParameter.QUERY,
        enum=["assigned lead", "in process", "opportunity", "qualification",
              "negotiation", "closed won", "closed lost", "closed"],
    ),
    OpenApiParameter("tags", OpenApiTypes.STR, OpenApiParameter.QUERY),

]


deal_detail_get_params = [
    organization_params_in_header,
    OpenApiParameter(
        "deal_attachment",
        OpenApiParameter.QUERY,
        OpenApiTypes.BINARY,
    ),
    OpenApiParameter("comment", OpenApiTypes.STR,OpenApiParameter.QUERY),
]

deal_comment_edit_params = [
    organization_params_in_header,
    OpenApiParameter("comment", OpenApiTypes.STR,OpenApiParameter.QUERY),
]

