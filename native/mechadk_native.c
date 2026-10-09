#if defined(_WIN32)
#define MECHADK_EXPORT __declspec(dllexport)
#else
#define MECHADK_EXPORT __attribute__((visibility("default")))
#endif

/* Stand-in for the OCaml code to come. The pointer is static; callers must not free it. */
MECHADK_EXPORT const char *mechadk_make_it_so(void)
{
    return "Make it so";
}
