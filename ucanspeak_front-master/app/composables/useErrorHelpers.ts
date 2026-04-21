import type { NuxtError } from "#app";

// never run it, with asyncData { lazy: true } option
export function useDataOrFail<
  T extends Awaited<ReturnType<typeof useAsyncData<any,NuxtError>>>
>
(asyncDataRes: T)
: T extends Awaited<ReturnType<typeof useAsyncData<infer R1,NuxtError>>> 
  ? Ref<Exclude<R1,undefined>> 
  : never
{
  const result = useCritical(asyncDataRes);
  return result.data as any;
}

export function useCritical<
  T extends Awaited<ReturnType<typeof useAsyncData<any,any>>>
>
(asyncDataRes: T)
{
  const result = asyncDataRes;
  
  watchError(result.error, (error) => {
    throw createError({
      ...error.value,
      fatal: true
    });
  });

  return result;
}

export function useWithAlert<
  T extends Awaited<ReturnType<typeof useAsyncData<any,any>>>
>(asyncDataRes: T, message?: string)
{
  if(import.meta.browser){


    watchError(asyncDataRes.error, () => {
      console.error(message);
    })
  }
  return asyncDataRes;
}

export function useHttpRequest<
    T extends Awaited<ReturnType<typeof useAsyncData<any,any>>>
>(asyncDataRes: T, message?: string)
{




    watchError(asyncDataRes.error, () => {
      console.error(message);

    })

  return asyncDataRes;
}


function checkError(error: Ref<NuxtError>, effect: (error: Ref<NuxtError>) => void){
  if(error.value){
    effect(error);
  }
}

function watchError(error: Ref<NuxtError>, effect: (error: Ref<NuxtError>) => void){
  checkError(error, effect);
  watch(error, () => effect(error));
}
